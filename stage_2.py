from pico2d import load_image
import game_world
import common
from rock import Rock
from poo import Poo


class Stage_2:
    def __init__(self):
        self.image = load_image('resource/rooms/Rooms_Basement-1.png')
        self.image2 = load_image('resource/objects/Door_1.png')

        self.rocks = []
        self.poos = []

        self.is_cleared = False


        self.manual_rock_positions = [
            (300, 380), (300, 460), (300, 540),  # 왼쪽 벽
            (700, 380), (700, 460), (700, 540),  # 오른쪽 벽

        ]

        self.manual_poo_positions = [
            (180, 250), (820, 250),
            (180, 600), (820, 600)
        ]
        # ==========================================

    def get_map_bounds(self):
        # 기본 맵 경계
        bounds = {
            'map_left': 100,
            'map_right': 875,
            'map_bottom': 175,
            'map_top': 700,
            'notches': []  # 기본은 닫힘
        }

        # 클리어 되었을 때만 노치(문 통로)를 개방
        if self.is_cleared:
            bounds['notches'] = [
                {'x': 490, 'y': 700, 'w': 50, 'h': 50},  # 위쪽 문
                {'x': 490, 'y': 175, 'w': 50, 'h': 50},  # 아래쪽 문
            ]

        return bounds
    def update(self):
        pass

    def draw(self):
        self.image.draw(250, 600, 500, 400)
        self.image.composite_draw(0, 'h', 750, 600, 500, 400)
        self.image.composite_draw(0, 'v', 250, 200, 500, 400)
        self.image.composite_draw(0, 'hv', 750, 200, 500, 400)


        if self.is_cleared:
            # 열린 문
            self.image2.clip_composite_draw(0, 40, 50, 52, 0, 'v', 500, 120, 120, 120)
            self.image2.clip_composite_draw(50, 40, 50, 52, 0, 'v', 465, 120, 130, 120)
            self.image2.clip_draw(0, 40, 50, 52, 500, 680, 120, 120)
            self.image2.clip_draw(50, 40, 50, 52, 465, 680, 130, 120)

        else:
            self.image2.clip_composite_draw(0, 40, 50, 52, 0, 'v', 500, 120, 120, 120)
            self.image2.clip_composite_draw(50, 0, 50, 52, 0, 'v', 465, 100, 130, 120)
            self.image2.clip_draw(0, 40, 50, 52, 500, 680, 120, 120)
            self.image2.clip_draw(50, 0, 50, 52, 465, 700, 130, 120)

    def ensure_obstacles(self):
        # 1. 객체 생성 (아직 리스트가 비어있다면)
        if not self.rocks and not self.poos:
            for (rx, ry) in self.manual_rock_positions:
                self.rocks.append(Rock(rx, ry))
            for (px, py) in self.manual_poo_positions:
                self.poos.append(Poo(px, py))

        # 2. 게임 월드에 추가 및 충돌 처리 등록
        # Rock
        for r in self.rocks:
            if r not in sum(game_world.world, []):  # 이미 없으면 추가
                game_world.add_object(r, 1)  # 장애물 레이어

            # 충돌 등록
            if common.isaac:
                game_world.add_collision_pair('isaac:rock', common.isaac, r)
            else:
                game_world.add_collision_pair('isaac:rock', None, r)
            game_world.add_collision_pair('rock:tear', r, None)

        # Poo
        for p in self.poos:
            if getattr(p, 'destroyed', False): continue
            if p not in sum(game_world.world, []):
                game_world.add_object(p, 1)

            if common.isaac:
                game_world.add_collision_pair('isaac:poo', common.isaac, p)
            else:
                game_world.add_collision_pair('isaac:poo', None, p)
            game_world.add_collision_pair('poo:tear', p, None)

    def clear_obstacles(self):
        # Rock 제거
        for r in self.rocks:
            game_world.remove_object(r)

        # Poo 제거
        for p in self.poos:
            game_world.remove_object(p)