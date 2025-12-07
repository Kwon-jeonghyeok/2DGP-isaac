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
        self.coins = []

        self.is_cleared = False

    def get_map_bounds(self):
        bounds = {
            'map_left': 100,
            'map_right': 1475,
            'map_bottom': 175,
            'map_top': 700,
            'clamp_margin': 90,
            'notches': []
        }

        #클리어 시에만 노치 개방
        if self.is_cleared:
            bounds['notches'] = [
                {'x': 1475, 'y': 400, 'w': 50, 'h': 70},  # 오른쪽 문
                {'x': 490, 'y': 175, 'w': 50, 'h': 50},  # 아래쪽 문
            ]
        return bounds

    def update(self):
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
            self.image.draw(sx, sy, 1375, 800)

        # 문 그리기
        if self.image2:
            door_world_x = 500
            door_world_y = 140
            dx, dy = game_world.world_to_screen(door_world_x, door_world_y)
            if self.is_cleared:
                # 열린 문 (기존 코드)
                self.image2.clip_composite_draw(0, 40, 50, 52, 0, 'v', dx, dy, 120, 120)
                dx2, dy2 = game_world.world_to_screen(465, 140)
                self.image2.clip_composite_draw(50, 40, 50, 52, 0, 'v', dx2, dy2, 130, 120)
            else:
                self.image2.clip_composite_draw(0, 40, 50, 52, 0, 'v', dx, dy, 120, 120)
                dx2, dy2 = game_world.world_to_screen(465, 120)
                self.image2.clip_composite_draw(50, 0, 50, 52, 0, 'v', dx2, dy2, 130, 120)
    def ensure_obstacles(self):
        if not self.rocks:
            self._create_rocks_and_poos(initial=(len(self.poos) == 0))
        else:
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
                game_world.add_collision_pair('rock:tear', r, None)
            except Exception:
                pass

        # 4) 아직 안 부서진 Poo 만 다시 월드에 추가
        for p in self.poos:
            if getattr(p, 'destroyed', False):
                continue
            if p in sum(game_world.world, []):
                continue
            try:
                game_world.add_object(p, 1)
                game_world.add_collision_pair('isaac:poo', None, p)
                game_world.add_collision_pair('poo:tear', p, None)
            except Exception:
                pass
        for c in self.coins:
            if c not in sum(game_world.world, []):
                game_world.add_object(c, 1)
                game_world.add_collision_pair('isaac:coin', common.isaac, c)

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
        thickness = 70.0  # Rock 크기

        half_w = frame_w / 2.0
        half_h = frame_h / 2.0

        self.rocks.clear()

        # Poo 위치 계산
        top_y = cy + half_h - thickness / 2.0
        bottom_y = cy - half_h + thickness / 2.0
        left_x = cx - half_w + thickness / 2.0 + 27
        right_x = cx + half_w - thickness / 2.0 - 27


        manual_offsets = [
            # top row
            (-335, top_y - cy + 20), (-249, top_y - cy + 20), (-163, top_y - cy + 20), (-77, top_y - cy + 20),
            (85, top_y - cy + 20), (171, top_y - cy + 20), (257, top_y - cy + 20), (343, top_y - cy + 20),

            # bottom row
            (-335, bottom_y - cy), (-249, bottom_y - cy), (-163, bottom_y - cy), (-77, bottom_y - cy),
            (85, bottom_y - cy), (171, bottom_y - cy), (257, bottom_y - cy), (343, bottom_y - cy),

            # left column
            (-335, -74), (-335, 86),

            # right column
            (343, -74), (343, 86),
        ]

        for dx, dy in manual_offsets:
            x = cx + dx
            y = cy + dy
            r = Rock(x, y, thickness, thickness)
            self.rocks.append(r)
            try:
                game_world.add_object(r, 1)
            except Exception:
                pass

        if initial:
            self.poos.clear()
            p_top = Poo(cx, top_y + 20)
            p_bottom = Poo(cx, bottom_y)
            p_left = Poo(left_x+3, cy)
            p_right = Poo(right_x+5, cy)
            self.poos.extend([p_top, p_bottom, p_left, p_right])

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
                pass
        for c in self.coins:
            game_world.remove_object(c)
