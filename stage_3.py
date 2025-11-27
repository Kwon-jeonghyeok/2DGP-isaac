from pico2d import load_image
import game_world

class Stage_3:
    def __init__(self):
        self.image = load_image('resource/rooms/Rooms_Caves_2.png')
        self.image2 = load_image('resource/objects/Door_1.png')

    def get_map_bounds(self):
        return {
            'map_left': 100,
            'map_right': 1500,
            'map_bottom': 175,
            'map_top': 700,
            'notches': [

                {'x': 1500, 'y': 400, 'w': 50, 'h': 70},
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
