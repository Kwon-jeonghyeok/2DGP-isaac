from pico2d import load_image


class Stage_2:
    def __init__(self):
        self.image = load_image('resource/rooms/Rooms_Basement-1.png')
        self.image2 = load_image('resource/objects/Door_1.png')

    def get_map_bounds(self):
        return {
            'map_left': 100,
            'map_right': 875,
            'map_bottom': 175,
            'map_top': 700,
            'notches': [

                {'x': 875, 'y': 400, 'w': 50, 'h': 70},
                {'x': 490, 'y': 175, 'w': 50, 'h': 50},
            ]
        }


    def update(self):
        pass

    def draw(self):
        self.image.draw(250, 600,500,400)
        self.image.composite_draw(0,'h',750,600,500,400)
        self.image.composite_draw(0,'v',250,200,500,400)
        self.image.composite_draw(0,'hv',750,200,500,400)
        self.image2.clip_composite_draw(0, 40, 50, 52,0,'v' ,500, 120, 120, 120)
        self.image2.clip_composite_draw(50, 40, 50, 52,0,'v', 465, 120, 130, 120)


        pass
