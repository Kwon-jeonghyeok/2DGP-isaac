from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_s, SDLK_d, SDL_KEYUP, SDLK_a, SDLK_w, SDLK_SPACE
from state_machine import StateMachine
import game_world
import game_framework
from tear import Tear


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
def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


#아이작 속도
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

#아이작 애니메이션 속도
TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10



class Idle:
    def __init__(self, isaac):
        self.isaac = isaac
    def enter(self,e):
        self.isaac.x_dir = 0
        self.isaac.y_dir = 0

    def exit(self, e):
        if space_down(e):
            self.isaac.fire_tear()
    def do(self):
        pass
    def draw(self):
        # 몸통
        self.isaac.image.clip_draw(0, 850, 40, 30, self.isaac.x, self.isaac.y - 35, 80, 60)
        #머리
        self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y,90,75)


class Walk:
    def __init__(self, isaac):
        self.isaac = isaac

    def update_direction(self):
        keys = self.isaac.pressed_keys
        last = getattr(self.isaac, 'last_key', None)

        # 수평
        if 'left' in keys and 'right' in keys:
            self.isaac.x_dir = -1 if last == 'left' else 1
        elif 'left' in keys:
            self.isaac.x_dir = -1
        elif 'right' in keys:
            self.isaac.x_dir = 1
        else:
            self.isaac.x_dir = 0

        # 수직
        if 'up' in keys and 'down' in keys:
            self.isaac.y_dir = 1 if last == 'up' else -1
        elif 'up' in keys:
            self.isaac.y_dir = 1
        elif 'down' in keys:
            self.isaac.y_dir = -1
        else:
            self.isaac.y_dir = 0

        # face_dir 결정: 수평 우선, 없으면 수직
        if self.isaac.x_dir != 0:
            self.isaac.face_dir = 1 if self.isaac.x_dir > 0 else -1
        elif self.isaac.y_dir != 0:
            self.isaac.face_dir = 2 if self.isaac.y_dir > 0 else 0

    def enter(self, e):
        self.update_direction()

    def exit(self, e):
        if space_down(e):
            self.isaac.fire_tear()

    def do(self):
        self.update_direction()
        self.isaac.frame = (self.isaac.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10
        self.isaac.x += self.isaac.x_dir * RUN_SPEED_PPS * game_framework.frame_time
        self.isaac.y += self.isaac.y_dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.isaac.face_dir == 1:  # right
            self.isaac.image.clip_draw(int(self.isaac.frame) * 32 , 810, 40, 26, self.isaac.x, self.isaac.y - 35, 80, 52)
            self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)
        elif self.isaac.face_dir == -1:  # left
            self.isaac.image.clip_composite_draw(int(self.isaac.frame) * 32, 810, 40, 26,0,'h', self.isaac.x+14, self.isaac.y - 35, 80, 52)
            self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)
        elif self.isaac.face_dir == 0 or self.isaac.face_dir == 2:  #위 아래 애니메이션 동일
            self.isaac.image.clip_draw(int(self.isaac.frame) * 32 , 853, 40, 26, self.isaac.x, self.isaac.y - 35, 80, 52)
            self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)


class Isaac:
    def __init__(self):
        self.x, self.y = 500, 400
        self.keydown = 0
        self.pressed_keys = set()
        self.last_key = None
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.x_dir = 0
        self.y_dir = 0


        self.tear_reload = 0.5  # 재장전 시간(초)
        self.tear_cooldown = 0.0  # 남은 쿨다운(초)

        self.image = load_image('resource/isaac.png')

        self.IDLE = Idle(self)
        self.WALK = Walk(self)

        # 맵 전체 경계
        self.map_left = 50
        self.map_right = 950
        self.map_bottom = 150
        self.map_top = 750

        self.half_width = 45
        self.half_height = 37

        self.notch_width = 200
        self.notch_height = 40

        keys_tuple = (SDLK_a, SDLK_d, SDLK_w, SDLK_s)

        def any_keydown(e):
            return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key in keys_tuple

        def to_idle_when_no_keys(e):
            return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and self.keydown == 0

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {space_down: self.IDLE, right_down: self.WALK, left_down: self.WALK, up_down: self.WALK, down_down: self.WALK},
                self.WALK: {space_down: self.WALK, to_idle_when_no_keys: self.IDLE}
            }
        )

    def update(self):
        self.state_machine.update()
        if self.tear_cooldown > 0.0:
            self.tear_cooldown = max(0.0, self.tear_cooldown - game_framework.frame_time)
        # 경계 처리
        # 기본 맵 사각형 내부로 클램프(노치 포함 시 조건부로 Y 허용 범위 확장)
        min_x = self.map_left + self.half_width
        max_x = self.map_right - self.half_width
        min_y = self.map_bottom + self.half_height

        # 기본 상단 한계 (노치가 없을 때)
        default_max_y = self.map_top - self.half_height

        # 노치의 가로 범위 계산(중앙 정렬)
        notch_left = (self.map_left + self.map_right) / 2 - self.notch_width / 2
        notch_right = notch_left + self.notch_width

        # 노치가 위로 확장되어 있다면 노치 상단까지 허용
        notch_top = self.map_top + self.notch_height
        notch_max_y = notch_top - self.half_height

        # 플레이어의 중심 x가 노치 가로 범위에 들어오면 상단 한계를 노치 상단까지 확장
        if (self.x > notch_left + self.half_width) and (self.x < notch_right - self.half_width):
            max_y = max(default_max_y, notch_max_y)
        else:
            max_y = default_max_y


        # 최종 클램프
        self.x = max(min_x, min(self.x, max_x))
        self.y = max(min_y, min(self.y, max_y))
        if self.y > 720:
            game_world.Stage =2


    def draw(self):
        self.state_machine.draw()

    def fire_tear(self):
        if self.tear_cooldown <= 0.0:
            tear = Tear(self.x, self.y, self.face_dir)
            game_world.add_object(tear, 1)
            self.tear_cooldown = self.tear_reload



    def handle_event(self, event):

        keymap = {
            SDLK_a: 'left',
            SDLK_d: 'right',
            SDLK_w: 'up',
            SDLK_s: 'down'
        }


        if event.type == SDL_KEYDOWN and event.key in keymap:
            kn = keymap[event.key]
            if kn not in self.pressed_keys:
                self.pressed_keys.add(kn)
                self.keydown += 1
            self.last_key = kn

        elif event.type == SDL_KEYUP and event.key in keymap:
            kn = keymap[event.key]
            if kn in self.pressed_keys:
                self.pressed_keys.remove(kn)
                self.keydown = max(0, self.keydown - 1)
            if self.last_key == kn:
                if self.pressed_keys:
                    self.last_key = next(iter(self.pressed_keys))
                else:
                    self.last_key = None

        self.state_machine.handle_state_event(('INPUT', event))
