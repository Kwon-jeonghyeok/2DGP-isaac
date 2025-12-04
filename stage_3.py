from pico2d import load_image
import game_world
import common
from rock import Rock
from poo import Poo


class Stage_3:
    def __init__(self):
        # 배경, 문 이미지 로드
        try:
            self.image = load_image('resource/rooms/Rooms_Caves_2.png')
        except Exception:
            self.image = None

        try:
            self.image2 = load_image('resource/objects/Door_1.png')
        except Exception:
            self.image2 = None

        # Rock 과 Poo 를 분리 관리
        self.rocks = []
        self.poos = []

    def get_map_bounds(self):
        return {
            'map_left': 100,
            'map_right': 1475,
            'map_bottom': 175,
            'map_top': 700,
            'notches': [
                {'x': 1475, 'y': 400, 'w': 50, 'h': 70},
                {'x': 490, 'y': 175, 'w': 50, 'h': 50},
            ]
        }

    def update(self):
        # Stage\_3 자체는 별도 업데이트 없음
        pass

    def draw(self):
        bounds = self.get_map_bounds()
        left = bounds['map_left']
        right = bounds['map_right']
        bottom = bounds['map_bottom']
        top = bounds['map_top']

        map_w = right - left
        map_h = top - bottom
        center_x = left + map_w / 2.0
        center_y = bottom + map_h / 2.0

        sx, sy = game_world.world_to_screen(center_x, center_y)
        if self.image:
            # 세로는 화면 높이(800)에 맞추고, 가로는 맵 폭에 맞춤
            self.image.draw(sx, sy, map_w, 800)

        # 문 그리기(월드 좌표 기준 -> 스크린 보정)
        if self.image2:
            door_world_x = 500
            door_world_y = 120
            dx, dy = game_world.world_to_screen(door_world_x, door_world_y)
            self.image2.clip_composite_draw(0, 40, 50, 52, 0, 'v', dx, dy, 120, 120)

            dx2, dy2 = game_world.world_to_screen(465, 120)
            self.image2.clip_composite_draw(50, 40, 50, 52, 0, 'v', dx2, dy2, 130, 120)

    def ensure_obstacles(self):
        # 1) Rock 이 비어 있으면 새로 생성
        if not self.rocks:
            self._create_rocks_and_poos(initial=(len(self.poos) == 0))
        else:
            # Rock 이 이미 있다면, 월드에 다시 추가만 필요할 수 있음
            for r in self.rocks:
                try:
                    game_world.add_object(r, 1)
                except Exception:
                    pass

        # 2) 충돌 그룹 기본 등록
        if common.isaac is not None:
            game_world.add_collision_pair('isaac:rock', common.isaac, None)
            game_world.add_collision_pair('isaac:poo', common.isaac, None)
        else:
            game_world.add_collision_pair('isaac:rock', None, None)
            game_world.add_collision_pair('isaac:poo', None, None)
        game_world.add_collision_pair('poo:tear', None, None)

        # 3) Rock 충돌쌍 등록
        for r in self.rocks:
            try:
                game_world.add_collision_pair('isaac:rock', None, r)
            except Exception:
                pass

        # 4) 아직 안 부서진 Poo 만 다시 월드에 추가
        for p in self.poos:
            if getattr(p, 'destroyed', False):
                # 이미 부서진 Poo 는 다시 추가하지 않음
                continue
            if p in sum(game_world.world, []):
                continue
            try:
                game_world.add_object(p, 1)
                game_world.add_collision_pair('isaac:poo', None, p)
                game_world.add_collision_pair('poo:tear', p, None)
            except Exception:
                pass

    def _create_rocks_and_poos(self, initial=True):

        bounds = self.get_map_bounds()
        left = bounds.get('map_left', 100)
        right = bounds.get('map_right', 1475)
        bottom = bounds.get('map_bottom', 175)
        top = bounds.get('map_top', 700)

        cx = (left + right) / 2.0
        cy = (bottom + top) / 2.0

        frame_w = 800.0
        frame_h = 360.0
        thickness = 60.0

        half_w = frame_w / 2.0
        half_h = frame_h / 2.0

        # Rock 리스트는 새로 구성
        self.rocks.clear()

        # Poo 위치 계산 (사용자 변경 X)
        top_y = cy + half_h - thickness / 2.0
        bottom_y = cy - half_h + thickness / 2.0
        left_x = cx - half_w + thickness / 2.0
        right_x = cx + half_w - thickness / 2.0

        # 수동 오프셋 목록 (cx, cy 기준). 직접 수정해서 원하는 좌표를 하나하나 지정할 수 있음.
        # 각 항목은 (dx, dy)로, 실제 좌표는 (cx + dx, cy + dy).
        # 예: ( -380, top_offset ) 같은 방식으로 직관적으로 배치 가능.
        top_offset = top_y - cy
        bottom_offset = bottom_y - cy

        manual_offsets = [
            # top row (dx, top_offset)
            (-380, top_offset), (-284, top_offset), (-188, top_offset), (-92, top_offset),
            (100, top_offset), (196, top_offset), (292, top_offset),(388 , top_offset),

            # bottom row
            (-380, bottom_offset), (-284, bottom_offset), (-188, bottom_offset), (-92, bottom_offset),
            (100, bottom_offset), (196, bottom_offset), (292, bottom_offset),(388, bottom_offset),

            # left column (left_offset, dy)
             (-380, -64),(-380, 76),

            # right column (right_offset, dy)
            (388, -64), (388, 76),
        ]

        # Poo 좌표 목록(겹침 방지용)
        poo_positions = {
            (round(cx, 3), round(top_y, 3)),
            (round(cx, 3), round(bottom_y, 3)),
            (round(left_x, 3), round(cy, 3)),
            (round(right_x, 3), round(cy, 3)),
        }

        eps = 1e-2

        # manual_offsets를 실제 좌표로 변환하여 Rock 생성
        for dx, dy in manual_offsets:
            x = cx + dx
            y = cy + dy
            # Poo 위치와 겹치면 건너뜀
            key = (round(x, 3), round(y, 3))
            if key in poo_positions:
                continue
            r = Rock(x, y, thickness, thickness)
            self.rocks.append(r)
            try:
                game_world.add_object(r, 1)
            except Exception:
                pass

        # Poo 는 처음 진입(initial=True)일 때만 생성
        if initial:
            self.poos.clear()
            p_top = Poo(cx, top_y)
            p_bottom = Poo(cx, bottom_y)
            p_left = Poo(left_x, cy)
            p_right = Poo(right_x, cy)
            self.poos.extend([p_top, p_bottom, p_left, p_right])

            # 아직 안 부서진 상태이므로 바로 월드에 추가
            for p in self.poos:
                try:
                    game_world.add_object(p, 1)
                    if common.isaac is not None:
                        game_world.add_collision_pair('isaac:poo', common.isaac, p)
                    else:
                        game_world.add_collision_pair('isaac:poo', None, p)
                    game_world.add_collision_pair('poo:tear', p, None)
                except Exception:
                    pass

    def clear_obstacles(self):

        # Rock 완전 제거
        for r in list(self.rocks):
            try:
                game_world.remove_object(r)
            except Exception:
                pass
        self.rocks.clear()

        # Poo 는 월드에서만 제거, 리스트는 유지
        for p in list(self.poos):
            try:
                game_world.remove_object(p)
            except Exception:
                # 이미 제거된 경우 등은 무시
                pass
