from pico2d import load_image
import game_world
import common
from rock import Rock
from poo import Poo

class Stage_3:
    def __init__(self):
        self.image = load_image('resource/rooms/Rooms_Caves_2.png')
        self.image2 = load_image('resource/objects/Door_1.png')
        self._create_central_frame()

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
        pass

    def draw(self):
        bounds = self.get_map_bounds()
        left = bounds['map_left']
        right = bounds['map_right']
        bottom = bounds['map_bottom']
        top = bounds['map_top']

        # 맵 실제 크기 계산
        map_w = right - left
        map_h = top - bottom
        center_x = left + map_w / 2.0
        center_y = bottom + map_h / 2.0

        # 월드->스크린 보정 후, 맵 크기 그대로 한 번만 그림
        sx, sy = game_world.world_to_screen(center_x, center_y)
        self.image.draw(sx, sy, map_w, 800)

        # 문 등 고정 오브젝트는 월드 좌표 보정하여 그림
        door_world_x = 500
        door_world_y = 120
        dx, dy = game_world.world_to_screen(door_world_x, door_world_y)
        self.image2.clip_composite_draw(0, 40, 50, 52, 0, 'v', dx, dy, 120, 120)

        dx2, dy2 = game_world.world_to_screen(465, 120)
        self.image2.clip_composite_draw(50, 40, 50, 52, 0, 'v', dx2, dy2, 130, 120)

        #self.image.draw(250, 600,500,400)
        #self.image.composite_draw(0,'h',750,600,500,400)
        #self.image.composite_draw(0,'v',250,200,500,400)
        #self.image.composite_draw(0,'hv',750,200,500,400)
        #self.image2.clip_composite_draw(0, 40, 50, 52,0,'v' ,500, 120, 120, 120)
        #self.image2.clip_composite_draw(50, 40, 50, 52,0,'v', 465, 120, 130, 120)


        pass

    def _create_central_frame(self):
        bounds = self.get_map_bounds()
        left = bounds.get('map_left', 100)
        right = bounds.get('map_right', 1500)
        bottom = bounds.get('map_bottom', 175)
        top = bounds.get('map_top', 700)

        cx = (left + right) / 2.0
        cy = (bottom + top) / 2.0

        frame_w = 800.0
        frame_h = 360.0
        thickness = 40.0
        spacing = 48.0

        half_w = frame_w / 2.0
        half_h = frame_h / 2.0

        rocks = []
        poos = []

        # top side
        x = cx - half_w + thickness / 2.0
        while x <= cx + half_w - thickness / 2.0:
            rocks.append(Rock(x, cy + half_h - thickness / 2.0, thickness, thickness))
            x += spacing

        # bottom side
        x = cx - half_w + thickness / 2.0
        while x <= cx + half_w - thickness / 2.0:
            rocks.append(Rock(x, cy - half_h + thickness / 2.0, thickness, thickness))
            x += spacing

        # left side
        y = cy - half_h + thickness / 2.0
        while y <= cy + half_h - thickness / 2.0:
            rocks.append(Rock(cx - half_w + thickness / 2.0, y, thickness, thickness))
            y += spacing

        # right side
        y = cy - half_h + thickness / 2.0
        while y <= cy + half_h - thickness / 2.0:
            rocks.append(Rock(cx + half_w - thickness / 2.0, y, thickness, thickness))
            y += spacing

        # 면 중앙에 Poo 배치 (top, bottom, left, right)
        poos.append(Poo(cx, cy + half_h - thickness / 2.0))
        poos.append(Poo(cx, cy - half_h + thickness / 2.0))
        poos.append(Poo(cx - half_w + thickness / 2.0, cy))
        poos.append(Poo(cx + half_w - thickness / 2.0, cy))

        # 충돌 그룹 생성(가능하면 Isaac 객체로 초기화)
        if common.isaac is not None:
            game_world.add_collision_pair('isaac:rock', common.isaac, None)
            game_world.add_collision_pair('isaac:poo', common.isaac, None)
        else:
            # Isaac이 아직 없으면 키만 생성
            game_world.add_collision_pair('isaac:rock', None, None)
            game_world.add_collision_pair('isaac:poo', None, None)

        # Poo가 Tear과 충돌하도록 그룹 생성 (left에 poo 추가)
        game_world.add_collision_pair('poo:tear', None, None)

        # 게임월드에 추가 및 충돌페어 등록
        for r in rocks:
            game_world.add_object(r, 1)
            game_world.add_collision_pair('isaac:rock', None, r)

        for p in poos:
            game_world.add_object(p, 1)
            game_world.add_collision_pair('isaac:poo', None, p)
            # poo:tear의 왼쪽에 poo 등록
            game_world.add_collision_pair('poo:tear', p, None)
