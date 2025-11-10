from pico2d import *
import game_world
import game_framework

PIXEL_PER_METER = (1.0 / 0.03)

class Tear:
    image = None
    def __init__(self, x=400, y=300, velocity=1):
        if Tear.image == None:
            Tear.image = load_image('resourse/objects/tears.png')
        self.x, self.y, self.velocity = x, y, velocity

    def draw(self):
        self.image.clip_draw(0, 300, 40, 35, self.x, self.y, 90, 75)

    def update(self):
        self.x += self.velocity

        if self.x < 25 or self.x > 800 - 25:
            game_world.remove_object(self)