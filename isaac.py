from pico2d import load_image, get_time , draw_rectangle, load_font
from sdl2 import SDL_KEYDOWN, SDLK_s, SDLK_d, SDL_KEYUP, SDLK_a, SDLK_w, SDLK_SPACE
from state_machine import StateMachine
import game_world
import game_framework
from tear import Tear
import common


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
            self.isaac.tear_y = self.isaac.tear_y*-1
            self.isaac.fire_tear()
    def do(self):
        pass
    def draw(self):

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
            self.isaac.tear_y = self.isaac.tear_y*-1
            self.isaac.fire_tear()

    def do(self):
        self.update_direction()
        self.isaac.frame = (self.isaac.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10
        self.isaac.x += self.isaac.x_dir * RUN_SPEED_PPS * game_framework.frame_time
        self.isaac.y += self.isaac.y_dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):

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
        self.pet = None
        self.damage = 1
        self.tear_y = 10
        #코인 개수 및 폰트 로드

        self.is_dying = False
        self.death_timer = 0.0

        #self.coin_count = 0
        self.coin_count =30 #초기 코인 개수 테스트용
        try:
            self.font = load_font('resource/upheaval-tt-brk.upheaval-tt-brk.ttf', 24)
        except Exception:
            self.font = None

        # 코인 아이콘 이미지 (UI용)
        try:
            self.coin_ui_image = load_image('resource/objects/coin.png')
        except:
            self.coin_ui_image = None
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
        self.map_left = 100
        self.map_right = 950
        self.map_bottom = 150
        self.map_top = 700

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
        if self.is_dying:
            self.death_timer += game_framework.frame_time
            # 2초 후 타이틀로 (애니메이션 1초 + 대기 1초)
            if self.death_timer > 2.0:
                self.hp = 0
            if self.death_timer < 1.0:
                self.frame = self.death_timer * 3
            else:
                self.frame = 2  # 마지막 프레임 고정

            return
        self.prev_x, self.prev_y = self.x, self.y
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
        bottom = bounds.get('map_bottom', -1e9) +25
        top = bounds.get('map_top', 1e9) + 25

        margin = bounds.get('clamp_margin', 0)
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

        if not allow_left and px < left + margin:
            self.x = left + margin
        if not allow_right and px > right - margin:
            self.x = right - margin
        if not allow_bottom and py < bottom:
            self.y = bottom
        if not allow_top and py > top:
            self.y = top

    def get_bb(self):
        return self.x - 23, self.y - 55, self.x + 40, self.y + 20



    def draw(self):
        self.draw_hp()
        self.draw_coin_ui()
        if self.is_dying:
            sx, sy = game_world.world_to_screen(self.x, self.y)
            frame_idx = int(self.frame)
            if frame_idx > 2: frame_idx = 2

            # 죽을 때 방향에 맞춰 그리기
            if self.face_dir == -1:
                self.image.clip_composite_draw(
                    frame_idx * 64,620, 64, 47,
                    0, 'h', sx, sy, 120, 95
                )
            else:
                self.image.clip_draw(
                    frame_idx * 64,620, 64, 47,
                    sx, sy, 120, 95
                )
            return  # 기존 그리기 건너뜀
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

    def draw_coin_ui(self):
        # 화면 좌측 상단
        ui_x, ui_y = 50, 750

        # 코인 아이콘 그리기
        if self.coin_ui_image:
            self.coin_ui_image.draw(ui_x, ui_y, 30, 30)

        # 숫자 그리기
        if self.font:
            self.font.draw(ui_x + 25, ui_y, f'x {self.coin_count}', (255, 255, 255))

    def fire_tear(self):
        if self.is_invulnerable:
            return
        if self.tear_cooldown <= 0.0:
            tear = Tear(self.x + self.tear_y + 20, self.y + self.tear_y, self.face_dir, damage= self.damage)
            game_world.add_object(tear, 1)
            game_world.add_collision_pair('host:tear', None, tear)
            game_world.add_collision_pair('sucker:tear', None, tear)
            game_world.add_collision_pair('poo:tear', None, tear)
            game_world.add_collision_pair('rock:tear', None, tear)
            game_world.add_collision_pair('charger:tear', None, tear)
            game_world.add_collision_pair('boss:tear', None, tear)
            game_world.add_collision_pair('lilhaunt:tear', None, tear)


            if self.pet:
                self.pet.fire_tear(self.face_dir, self.damage)
            self.tear_cooldown = self.tear_reload

    def draw_hp(self):
        total_hearts = 5
        # 죽어가는 중(0.1)에도 HP는 0으로 보이게 처리
        display_hp = self.hp
        if self.is_dying: display_hp = 0

        hp = max(0, min(self.max_hp, display_hp))
        cols = 3
        frame_w = int(self.hearts_image.w // cols)
        frame_h = int(self.hearts_image.h)
        start_x, start_y = 80, 720
        spacing, scale = frame_w // 6, 2
        for i in range(total_hearts):
            heart_hp = max(0, min(2, hp - i * 2))
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
        if self.is_dying: return self.hp
        if self.is_invulnerable:
            return self.hp
        old_hp = getattr(self, 'hp', 0)
        potential_hp = old_hp - abs(int(amount))
        if potential_hp <= 0:
            self.hp = 0.1  # 0.1로 고정하여 play_mode에서 삭제되는 것 방지
            self.is_dying = True
            self.death_timer = 0.0
            game_world.remove_collision_object(self)  # 충돌 판정 제거
            print("Isaac started dying animation...")
            return 0.1
        self.hp = potential_hp

        if self.hp < old_hp:
            self.is_invulnerable = True
            self.hurt_timer = self.hurt_duration
            self._hurt_blink_acc = 0.0
            self.hurt_visible = True
        return self.hp
        return applied
    def heal(self, amount):
        return self.change_hp(abs(int(amount)))

    def is_dead(self):
        return getattr(self, 'hp', 0) <= 0

    def handle_event(self, event):
        if self.is_dying: return
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
        # 기존 피해 처리: self.take_damage 그대로 유지
        if self.is_dying: return

        if group in ('isaac:host', 'host_bullet:isaac', 'isaac:sucker', 'isaac:charger', 'isaac:lilhaunt', 'isaac:boss',
                     'isaac:boss_bullet'):
            try:
                self.take_damage(1)
            except Exception:
                pass
            return
        if group in ('isaac:boss_laser'):
            try:
                self.take_damage(2)
            except Exception:
                pass
            return
        if group == 'isaac:coin':
            self.coin_count += 1
            return

        if group == 'isaac:hp_potion':
            # 체력 회복 (최대 체력까지만)
            if self.hp < self.max_hp:
                self.heal(2)  # 하트 1칸(2 HP) 회복
            return  # 물약은 획득 후 사라짐 (HPPotion 쪽에서 remove_object 호출됨)
        # 장애물(Rock, Poo) 충돌: 최소 보정 + 너무 작은 보정은 무시해서 흔들림 제거
        if group == 'isaac:damage_item':
            # other는 DamageItem 객체
            if self.coin_count >= other.price:
                self.coin_count -= other.price
                self.damage += 1  # 공격력 증가

                # [핵심 추가] 현재 스테이지에 '팔렸음'을 기록
                if common.stage and hasattr(common.stage, 'item_sold'):
                    common.stage.item_sold = True

                # 아이템 제거
                game_world.remove_object(other)
            return
        if group in ('isaac:rock', 'isaac:poo'):
            try:
                if other is None:
                    return
                if not hasattr(other, 'get_bb') or not hasattr(self, 'get_bb'):
                    return

                l_a, b_a, r_a, t_a = self.get_bb()
                l_b, b_b, r_b, t_b = other.get_bb()

                overlap_x = min(r_a, r_b) - max(l_a, l_b)
                overlap_y = min(t_a, t_b) - max(b_a, b_b)

                # 실제로 겹치지 않으면 무시
                if overlap_x <= 0 or overlap_y <= 0:
                    return

                # 아주 작은 보정은 카메라에 거의 안 보이게 무시
                MIN_SEPARATION = 0.8  # 이 값보다 작으면 보정 안 함
                EPS = 0.1  # 겹침 방지용 아주 작은 여유

                # 이전 위치 없으면 현재 위치 기준으로만 처리
                prev_x = getattr(self, 'prev_x', self.x)
                prev_y = getattr(self, 'prev_y', self.y)

                # Isaac의 중심
                center_ax = (l_a + r_a) / 2.0
                center_ay = (b_a + t_a) / 2.0
                center_bx = (l_b + r_b) / 2.0
                center_by = (b_b + t_b) / 2.0

                # 실제 이동량(이전 프레임 대비)
                dx = self.x - prev_x
                dy = self.y - prev_y

                # 어떤 축으로 밀어낼지 결정: 더 작은 침투 축, 단 이동이 거의 없으면 보정하지 않음
                if overlap_x < overlap_y:
                    # 수평으로만 분리
                    if abs(overlap_x) < MIN_SEPARATION:
                        # 미세한 떨림 방지: 보정 안 하고 이전 위치로 롤백
                        self.x = prev_x
                        return

                    if center_ax < center_bx:
                        # Isaac이 왼쪽 -> 왼쪽으로 되돌리거나 왼쪽으로 약간 스냅
                        self.x -= (overlap_x + EPS)
                    else:
                        # Isaac이 오른쪽 -> 오른쪽으로 되돌리거나 오른쪽으로 약간 스냅
                        self.x += (overlap_x + EPS)
                else:
                    # 수직으로만 분리
                    if abs(overlap_y) < MIN_SEPARATION:
                        self.y = prev_y
                        return

                    if center_ay < center_by:
                        # Isaac이 아래
                        self.y -= (overlap_y + EPS)
                    else:
                        # Isaac이 위
                        self.y += (overlap_y + EPS)

                # 맵 경계가 있다면 다시 한 번 클램프
                try:
                    if common.stage and hasattr(common.stage, 'get_map_bounds'):
                        bounds = common.stage.get_map_bounds()
                        self.apply_map_bounds(bounds)
                except Exception:
                    pass

                except Exception:
                    pass
                return

            except Exception:
                pass
            return

        # 그 외 그룹은 무시
        return
