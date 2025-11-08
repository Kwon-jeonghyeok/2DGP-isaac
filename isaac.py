from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_s, SDLK_d, SDL_KEYUP, SDLK_a, SDLK_w
from state_machine import StateMachine
import game_world
import game_framework


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d
def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a
def up_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_w
def up_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_w
def down_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s
def down_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_s

#아이작 속도
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

#아이작 애니메이션 속도
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10



class Idle:
    def __init__(self, isaac):
        self.isaac = isaac
    def enter(self,e):
        self.isaac.x_dir = 0
        self.isaac.y_dir = 0


    def exit(self,e):
        pass
    def do(self):
        pass
    def draw(self):
        # 몸통
        self.isaac.image.clip_draw(0, 850, 40, 30, self.isaac.x, self.isaac.y - 35, 90, 80)
        #머리
        self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y,90,75)


class Walk:
    def __init__(self, isaac):
        self.isaac = isaac
    def enter(self,e):
        if right_down(e):
           self.isaac.x_dir = self.isaac.face_dir =1
        if left_down(e) :
            self.isaac.x_dir = self.isaac.face_dir  =-1
        if up_down(e):
           self.isaac.face_dir = 2
           self.isaac.y_dir = 1
        if down_down(e):
            self.isaac.face_dir = 0
            self.isaac.y_dir = -1



    def exit(self,e):
        pass

    def do(self):
        self.isaac.frame = (self.isaac.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10
        self.isaac.x += self.isaac.x_dir * RUN_SPEED_PPS * game_framework.frame_time
        self.isaac.y += self.isaac.y_dir * RUN_SPEED_PPS * game_framework.frame_time


    def draw(self):
        if self.isaac.face_dir == 1:  # right
            self.isaac.image.clip_draw(int(self.isaac.frame) * 40, 850, 40, 30, self.isaac.x, self.isaac.y - 35, 90, 80)
            self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)
        elif self.isaac.face_dir == -1:  # left
            self.isaac.image.clip_draw(int(self.isaac.frame) * 40, 800, 40, 30, self.isaac.x, self.isaac.y - 35, 90, 80)
            self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)
        elif self.isaac.face_dir == 0:  # down
            self.isaac.image.clip_draw(int(self.isaac.frame) * 40, 950, 40, 30, self.isaac.x, self.isaac.y - 35, 90, 80)
            self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)
        elif self.isaac.face_dir == 2:  # up
            self.isaac.image.clip_draw(int(self.isaac.frame) * 40, 700, 40, 30, self.isaac.x, self.isaac.y - 35, 90, 80)
            self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)

class Isaac:
    def __init__(self):
        self.x, self.y = 500,400
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.x_dir = 0
        self.y_dir = 0
        #1 은 오른쪽 -1 은 왼쪽 0 은 아래 2는 위
        self.image = load_image('resourse/isaac.png')

        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.WALK, left_down: self.WALK, up_down: self.WALK, down_down: self.WALK
                            , right_up: self.WALK, left_up: self.WALK, up_up: self.WALK, down_up: self.WALK},
                self.WALK:{right_up: self.IDLE , left_up: self.IDLE, up_up: self.IDLE, down_up: self.IDLE,
                           right_down: self.IDLE, left_down: self.IDLE, up_down: self.IDLE, down_down: self.IDLE}
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
    def handle_event(self,event):
        self.state_machine.handle_state_event(('INPUT', event))