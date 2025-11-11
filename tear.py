from pico2d import *
import game_world
import game_framework

PIXEL_PER_METER = (1.0 / 0.015)

TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 4
class Tear:
    image = None
    def __init__(self, x=400, y=300, face_dir=1 ):
        if Tear.image == None:
            Tear.image = load_image('resource/objects/tears.png')
        self.x, self.y, self.dir = x, y, face_dir
        self.frame = 0

    def draw(self):
        self.image.clip_draw(280, 215, 30, 30, self.x, self.y, 40, 40)
        #self.image.clip_draw(int(self.frame)*32 + 300,215, 32, 30, self.x, self.y, 45, 45)

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 4

        if self.dir == 1:
            self.x +=  PIXEL_PER_METER * ACTION_PER_TIME * game_framework.frame_time * 5
        elif self.dir == -1:
            self.x -=  PIXEL_PER_METER * ACTION_PER_TIME * game_framework.frame_time * 5
        elif self.dir == 2:
            self.y +=  PIXEL_PER_METER * ACTION_PER_TIME * game_framework.frame_time * 5
        elif self.dir == 0:
            self.y -=  PIXEL_PER_METER * ACTION_PER_TIME * game_framework.frame_time * 5

        if self.x < 25 or self.x > 800 - 25:
            game_world.remove_object(self)