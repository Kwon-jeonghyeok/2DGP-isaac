from pico2d import load_image
import game_world
import common
from machine import Machine
from damage_item import DamageItem
from coin import Coin


class Stage_4:
    def __init__(self):
        self.image = load_image('resource/rooms/Rooms_Basement-1.png')
        self.image2 = load_image('resource/objects/Door_1.png')

        self.machine = None
        self.damage_item = None
        self.coins = []  # 스테이지에 떨어진 코인 관리용
        self.is_cleared = True  # 상점은 적이 없으므로 항상 클리어 상태
        self.item_sold = False

    def get_map_bounds(self):
        # Stage 1, 2와 동일한 기본 방 구조
        return {
            'map_left': 100,
            'map_right': 875,
            'map_bottom': 175,
            'map_top': 700,
            'notches': [
                # 들어온 문 (왼쪽 문이라고 가정 - Stage 3의 오른쪽에서 왔으므로)
                {'x': 100, 'y': 400, 'w': 50, 'h': 70},
            ]
        }

    def update(self):
        pass

    def draw(self):
        self.image.draw(250, 600, 500, 400)
        self.image.composite_draw(0, 'h', 750, 600, 500, 400)
        self.image.composite_draw(0, 'v', 250, 200, 500, 400)
        self.image.composite_draw(0, 'hv', 750, 200, 500, 400)

        # 왼쪽 문 (열린 상태)
        # 좌표: x=100, y=400
        dx, dy = game_world.world_to_screen(100, 400)
        self.image2.clip_composite_draw(0, 40, 50, 52, 3.14159 / 2, '', dx, dy, 120, 120)

    def ensure_obstacles(self):

        if not self.item_sold:
            if self.damage_item is None:
                self.damage_item = DamageItem(600, 500)

            if self.damage_item not in sum(game_world.world, []):
                game_world.add_object(self.damage_item, 1)
                game_world.add_collision_pair('isaac:damage_item', common.isaac, self.damage_item)
        # 머신 생성 (중앙)
        if self.machine is None:
            self.machine = Machine(500, 350)

        if self.machine not in sum(game_world.world, []):
            game_world.add_object(self.machine, 1)
            game_world.add_collision_pair('isaac:machine', common.isaac, self.machine)

        # 떨어진 코인 복구
        for c in self.coins:
            if c not in sum(game_world.world, []):
                game_world.add_object(c, 1)
                game_world.add_collision_pair('isaac:coin', common.isaac, c)

    def clear_obstacles(self):
        if self.machine:
            game_world.remove_object(self.machine)

        for c in self.coins:
            game_world.remove_object(c)
        if self.damage_item:
            game_world.remove_object(self.damage_item)