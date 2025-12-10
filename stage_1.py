from pico2d import load_image
import pico2d
from pico2d import *


class Stage_1:
    def __init__(self):
        self.image = load_image('resource/rooms/Rooms_Basement-1.png')
        self.image1 = load_image('resource/rooms/Rooms_Basement_2.png')
        self.image2 = load_image('resource/objects/Door_1.png')


    def get_map_bounds(self):
        return {
            'map_left': 100,
            'map_right': 875,
            'map_bottom': 175,
            'map_top': 700,
            'notches': [
                # 상단 중앙에 작은 노치 (위쪽 통로)
                {'x': 490, 'y': 700, 'w': 50, 'h': 50},
                # 좌측 중간에 작은 노치 (왼쪽 통로)
                #{'x': 100, 'y': 400, 'w': 50, 'h': 70},
            ]
        }

    def update(self):
        pass

    def draw(self):
        self.image.draw(250, 600,500,400)
        self.image.composite_draw(0,'h',750,600,500,400)
        self.image.composite_draw(0,'v',250,200,500,400)
        self.image.composite_draw(0,'hv',750,200,500,400)
        self.image1.draw(500, 400, 700, 300)
        self.image2.clip_draw(0,40,50,52,500,680,120,120)
        self.image2.clip_draw(50, 40, 50, 52, 465, 680, 130, 120)


        pass
