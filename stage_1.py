from pico2d import load_image


class Stage_1:
    def __init__(self):
        self.image = load_image('C:/Users/jhkwo/OneDrive/gitbub/2DGP-isaac/resourse/rooms/Rooms_Basement-1.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(250, 600,500,400)
        self.image.composite_draw(0,'h',750,600,500,400)
        self.image.composite_draw(0,'v',250,200,500,400)
        self.image.composite_draw(0,'hv',750,200,500,400)
        pass
