from pico2d import load_image


class Stage_2:
    def __init__(self):
        self.image = load_image('resource/rooms/Rooms_Basement-1.png')

    def get_map_bounds(self):
        return {
            'map_left': 100,
            'map_right': 875,
            'map_bottom': 175,
            'map_top': 700,
        }


    def update(self):
        pass

    def draw(self):
        self.image.draw(250, 600,500,400)
        self.image.composite_draw(0,'h',750,600,500,400)
        self.image.composite_draw(0,'v',250,200,500,400)
        self.image.composite_draw(0,'hv',750,200,500,400)



        pass
