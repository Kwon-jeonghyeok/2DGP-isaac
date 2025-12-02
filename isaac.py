from pico2d import load_image, get_time , draw_rectangle
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
        #self.isaac.image.clip_draw(0, 850, 40, 30, self.isaac.x, self.isaac.y - 35, 80, 60)
        #머리
        #self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y,90,75)

        sx, sy = game_world.world_to_screen(self.isaac.x, self.isaac.y - 35)
        self.isaac.image.clip_draw(0, 850, 40, 30, sx, sy, 80, 60)
        hx, hy = game_world.world_to_screen(self.isaac.x, self.isaac.y)
        self.isaac.image.clip_draw(0, 900, 40, 35, hx, hy, 90, 75)



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
        #if self.isaac.face_dir == 1:  # right
            #self.isaac.image.clip_draw(int(self.isaac.frame) * 32 , 810, 40, 26, self.isaac.x, self.isaac.y - 35, 80, 52)
            #self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)
        #elif self.isaac.face_dir == -1:  # left
            #self.isaac.image.clip_composite_draw(int(self.isaac.frame) * 32, 810, 40, 26,0,'h', self.isaac.x+14, self.isaac.y - 35, 80, 52)
            #self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)
        #elif self.isaac.face_dir == 0 or self.isaac.face_dir == 2:  #위 아래 애니메이션 동일
            #self.isaac.image.clip_draw(int(self.isaac.frame) * 32 , 853, 40, 26, self.isaac.x, self.isaac.y - 35, 80, 52)
            #self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y, 90, 75)

        if self.isaac.face_dir == 1:  # right
            sx, sy = game_world.world_to_screen(self.isaac.x, self.isaac.y - 35)
            self.isaac.image.clip_draw(int(self.isaac.frame) * 32 , 810, 40, 26, sx, sy, 80, 52)
            hx, hy = game_world.world_to_screen(self.isaac.x, self.isaac.y)
            self.isaac.image.clip_draw(0, 900, 40, 35, hx, hy, 90, 75)

        elif self.isaac.face_dir == -1:  # left (mirror)
            sx, sy = game_world.world_to_screen(self.isaac.x + 14, self.isaac.y - 35)  # +14 유지 (원래 코드와 동일한 시프트)
            self.isaac.image.clip_composite_draw(int(self.isaac.frame) * 32, 810, 40, 26, 0, 'h', sx, sy, 80, 52)
            hx, hy = game_world.world_to_screen(self.isaac.x, self.isaac.y)
            self.isaac.image.clip_draw(0, 900, 40, 35, hx, hy, 90, 75)

        else:  # 위/아래
            sx, sy = game_world.world_to_screen(self.isaac.x, self.isaac.y - 35)
            self.isaac.image.clip_draw(int(self.isaac.frame) * 32 , 853, 40, 26, sx, sy, 80, 52)
            hx, hy = game_world.world_to_screen(self.isaac.x, self.isaac.y)
            self.isaac.image.clip_draw(0, 900, 40, 35, hx, hy, 90, 75)


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
        self.max_hp = 10
        self.hp = self.max_hp
        self.hearts_image = load_image('resource/UI_Hearts.png')

        self.hurt_image = load_image('resource/hurt.png')
        self.is_invulnerable = False
        self.hurt_timer = 0.0
        self.hurt_duration = 1.0  # 무적 시간
        self.hurt_blink_interval = 0.12  # 깜빡임 간격
        self._hurt_blink_acc =0.0
        self.hurt_visible = True


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

        self.notch_width = 150
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
        # 무적 타이머 처리
        if self.hurt_timer > 0.0:
            dt = game_framework.frame_time
            self.hurt_timer = max(0.0, self.hurt_timer - dt)
            self._hurt_blink_acc += dt
            if self._hurt_blink_acc >= self.hurt_blink_interval:
                self._hurt_blink_acc -= self.hurt_blink_interval
                self.hurt_visible = not self.hurt_visible
            if self.hurt_timer == 0.0:
                self.is_invulnerable = False
                self.hurt_visible = True
                self._hurt_blink_acc = 0.0
        if self.hp == 0:
            game_world.remove_object(self)


    def apply_map_bounds(self, bounds):
        left = bounds.get('map_left', -1e9)
        right = bounds.get('map_right', 1e9)
        bottom = bounds.get('map_bottom', -1e9)
        top = bounds.get('map_top', 1e9)

        # 기본적으로 모든 가장자리를 막음(허용=False)
        allow_left = allow_right = allow_top = allow_bottom = False

        # 플레이어의 기준점으로 중심
        px, py = self.x, self.y

        # 노치가 명시되어 있으면 검사
        for n in bounds.get('notches', []):
            nx = n.get('x', 0)
            ny = n.get('y', 0)
            nw = n.get('w', 0)
            nh = n.get('h', 0)
            nx1 = nx - nw / 2.0
            nx2 = nx + nw / 2.0
            ny1 = ny - nh / 2.0
            ny2 = ny + nh / 2.0

            # 노치가 맵의 특정 가장자리에 닿아 있는지로 판단
            # top 노치: 노치 상단/하단 범위가 top에 접해 있고 플레이어 x가 노치 내에 있으면 통과 허용
            if ny1 <= top <= ny2:
                if nx1 <= px <= nx2:
                    allow_top = True
            # bottom 노치
            if ny1 <= bottom <= ny2:
                if nx1 <= px <= nx2:
                    allow_bottom = True
            # left 노치
            if nx1 <= left <= nx2:
                if ny1 <= py <= ny2:
                    allow_left = True
            # right 노치
            if nx1 <= right <= nx2:
                if ny1 <= py <= ny2:
                    allow_right = True

        # 노치로 허용되지 않은 가장자리들은 위치를 클램프
        if not allow_left and px < left:
            self.x = left
        if not allow_right and px > right:
            self.x = right
        if not allow_bottom and py < bottom:
            self.y = bottom
        if not allow_top and py > top:
            self.y = top

    def get_bb(self):
        return self.x - 30, self.y - 55, self.x + 45, self.y + 20



    def draw(self):
        self.draw_hp()
        if self.hurt_timer > 0.0:
            if self.hurt_visible:
                try:
                    #self.hurt_image.draw(self.x + 10, self.y - 10, 80, 80)
                    sx, sy = game_world.world_to_screen(self.x + 10, self.y - 10)
                    # hurt_image는 UI처럼 화면 상대일 수도 있지만 월드에 붙어있다면 보정
                    self.hurt_image.draw(sx, sy, 80, 80)
                except Exception:
                    pass
        else:
            # 평상시에는 기존 그리기와 HP UI를 그림
            self.state_machine.draw()

        #draw_rectangle(*self.get_bb())
        l, b, r, t = self.get_bb()
        ls, bs = game_world.world_to_screen(l, b)
        rs, ts = game_world.world_to_screen(r, t)
        draw_rectangle(ls, bs, rs, ts)

    def fire_tear(self):
        if self.is_invulnerable:
            return
        if self.tear_cooldown <= 0.0:
            tear = Tear(self.x, self.y, self.face_dir)
            game_world.add_object(tear, 1)
            game_world.add_collision_pair('host:tear', None, tear)
            game_world.add_collision_pair('sucker:tear', None, tear)
            game_world.add_collision_pair('poo:tear', None, tear)
            self.tear_cooldown = self.tear_reload

    def draw_hp(self):
        total_hearts = 5
        hp = max(0,min(self.max_hp, self.hp))
        cols = 3
        frame_w = int(self.hearts_image.w // cols)
        frame_h = int(self.hearts_image.h)

        start_x = 80
        start_y = 720

        spacing = frame_w // 6
        scale = 2

        for i in range(total_hearts):
            heart_hp = max(0,min(2, hp - i * 2))
            frame_idx = 2 - heart_hp
            sx = frame_idx * frame_w
            dx = start_x + i * (frame_w * scale + spacing)
            self.hearts_image.clip_draw(sx, 0, frame_w, frame_h, dx, start_y, frame_w * scale, frame_h * scale)

    def change_hp(self, delta):
        old = getattr(self, 'hp', 0)
        self.hp = max(0, min(self.max_hp, old + delta))
        # 죽음 처리 필요 시(예: if self.hp == 0: self.on_death())
        return self.hp

    def set_hp(self, value):
        self.hp = max(0, min(self.max_hp, int(value)))
        return self.hp

    def take_damage(self, amount):
        if self.is_invulnerable:
            return self.hp
        old_hp = getattr(self, 'hp', 0)
        applied = self.change_hp(-abs(int(amount)))
        if applied < old_hp:
            self.is_invulnerable = True
            self.hurt_timer = self.hurt_duration
            self._hurt_blink_acc = 0.0
            self.hurt_visible = True
        return applied
    def heal(self, amount):
        return self.change_hp(abs(int(amount)))

    def is_dead(self):
        return getattr(self, 'hp', 0) <= 0

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

    def handle_collision(self, group, other):
        # 기존 피해 처리: 기존 self.take_damage 유지
        if group in ('isaac:host', 'host_bullet:isaac', 'isaac:sucker'):
            try:
                self.take_damage(1)
            except Exception:
                pass
            return

        # 장애물(Rock, Poo)과의 충돌: 스냅 방식으로 보정하여 흔들림 최소화
        if group in ('isaac:rock', 'isaac:poo'):
            try:
                if other is None:
                    return
                if not hasattr(other, 'get_bb') or not hasattr(self, 'get_bb'):
                    return

                l_a, b_a, r_a, t_a = self.get_bb()
                l_b, b_b, r_b, t_b = other.get_bb()

                # 침투량 계산
                overlap_x = min(r_a, r_b) - max(l_a, l_b)
                overlap_y = min(t_a, t_b) - max(b_a, b_b)

                if overlap_x <= 0 or overlap_y <= 0:
                    return

                # 작은 진동을 제거하기 위한 임계값 및 여유
                TOLERANCE = 0.5  # 이보다 작은 침투는 스냅 처리
                EPS = 1.0  # 밖으로 떨어뜨리는 여유(진동 방지)

                # Isaac의 축별 오프셋(중심에서 각 엣지까지 거리)
                left_offset = self.x - l_a
                right_offset = r_a - self.x
                bottom_offset = self.y - b_a
                top_offset = t_a - self.y

                # 더 작은 축으로만 보정하되 '스냅'으로 위치를 정확히 엣지 바깥으로 설정
                if overlap_x < overlap_y:
                    # 수평 보정: Isaac의 중심을 비교하여 어느 쪽으로 밀어낼지 결정
                    center_ax = (l_a + r_a) / 2.0
                    center_bx = (l_b + r_b) / 2.0
                    if center_ax < center_bx:
                        # Isaac이 왼쪽 -> 오른쪽 장애물의 왼쪽 엣지 기준으로 오른쪽을 벗어나게 스냅
                        # r_a_new = l_b - EPS  => self.x = r_a_new - right_offset
                        self.x = (l_b - EPS) - right_offset
                    else:
                        # Isaac이 오른쪽 -> 왼쪽 엣지 기준으로 왼쪽을 벗어나게 스냅
                        # l_a_new = r_b + EPS => self.x = l_a_new + left_offset
                        self.x = (r_b + EPS) + left_offset
                else:
                    # 수직 보정
                    center_ay = (b_a + t_a) / 2.0
                    center_by = (b_b + t_b) / 2.0
                    if center_ay < center_by:
                        # Isaac이 아래 -> 위 장애물의 아래 엣지 기준으로 아래로 스냅
                        # t_a_new = b_b - EPS => self.y = t_a_new - top_offset
                        self.y = (b_b - EPS) - top_offset
                    else:
                        # Isaac이 위 -> 아래 엣지 기준으로 위로 스냅
                        # b_a_new = t_b + EPS => self.y = b_a_new + bottom_offset
                        self.y = (t_b + EPS) + bottom_offset

                # 아주 미세한 잔여 침투가 남았으면 추가로 한 번 더 스냅(안정성)
                try:
                    l_a2, b_a2, r_a2, t_a2 = self.get_bb()
                    if min(r_a2, r_b) - max(l_a2, l_b) > 0 and min(t_a2, t_b) - max(b_a2, b_b) > 0:
                        # 남아있으면 강제 완전 분리: 큰 EPS 로 한 번 더 밀어냄
                        BIG_EPS = 4.0
                        # 가로 우선으로 시도
                        if overlap_x <= overlap_y:
                            center_ax = (l_a2 + r_a2) / 2.0
                            center_bx = (l_b + r_b) / 2.0
                            if center_ax < center_bx:
                                self.x = (l_b - BIG_EPS) - (r_a2 - self.x)
                            else:
                                self.x = (r_b + BIG_EPS) + (self.x - l_a2)
                        else:
                            center_ay = (b_a2 + t_a2) / 2.0
                            center_by = (b_b + t_b) / 2.0
                            if center_ay < center_by:
                                self.y = (b_b - BIG_EPS) - (t_a2 - self.y)
                            else:
                                self.y = (t_b + BIG_EPS) + (self.y - b_a2)
                except Exception:
                    pass

                # 맵 경계 재적용(있으면)
                try:
                    bounds = None
                    for layer in game_world.world:
                        for o in layer:
                            if hasattr(o, 'get_map_bounds'):
                                try:
                                    bounds = o.get_map_bounds()
                                    break
                                except Exception:
                                    bounds = None
                        if bounds:
                            break
                    if bounds:
                        try:
                            self.apply_map_bounds(bounds)
                        except Exception:
                            pass
                except Exception:
                    pass

            except Exception:
                pass
            return

        # 그 외 그룹은 무시
        return


