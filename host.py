import game_framework
import game_world
import random

from pico2d import *

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

class Host:
    image = None
    def __init__(self):
        if Host.image == None:
            Host.image = load_image("resource/monster/Host.png")
        self.x, self.y = random.randint(180, 820), random.randint(150, 650)
        self.frame = 0.0
        self.hp = 3


    def get_bb(self):
        return self.x - 35, self.y - 75, self.x + 35, self.y
    def get_range_bb(self):
        return self.x - 175, self.y - 175, self.x + 175, self.y + 150

    def update(self):
        if self.hp <= 0:
            game_world.remove_object(self)
        pass
    def draw(self):
        self.image.clip_draw(0, 0, 32, 60, self.x, self.y, 70, 150)
        draw_rectangle(*self.get_bb())
        draw_rectangle(*self.get_range_bb())

    def handle_collision(self, group, other):
        if group == 'host:tear':
            self.hp -= 1
        pass
