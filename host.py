import game_framework
import game_world
import random
from pico2d import *
from coin import Coin
import common
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0


class Host:
    image = None
    _instances = []

    def __init__(self):
        if Host.image is None:
            try:
                Host.image = load_image("resource/monster/Host.png")
            except Exception:
                Host.image = None

        Host._instances.append(self)
        self.frame = 0.0
        self.hp = 3

        # 초기화 시 안전한 위치 찾기 실행
        # (x, y 좌표가 여기서 결정됨)
        self.set_safe_position()

        self.state = 'idle'
        self.align_tolerance = 40
        self.detect_range = 600
        self.attack_cooldown = 1.5
        self._cooldown_timer = 0.0

        self.attack_duration = 3.0
        self._attack_timer = 0.0
        self.shoot_interval = 0.25
        self._shoot_timer = 0.0

        self.is_vulnerable = False
        self._has_shot = False

        self.attack_frames = 3
        self.attack_frame_index = 0
        self._attack_anim_timer = 0.0

        self.fire_delay = 0.7
        self._fire_delay_timer = 0.0
        self._pending_shot = False
        self.attack_frame_durations = [0.5, 2.5, 1.0]

    def set_safe_position(self):
        """현재 월드 상태를 확인하여 장애물과 겹치지 않는 랜덤 위치로 이동"""
        max_attempts = 100
        attempt = 0
        found = False

        # 맵 내부 스폰 가능 범위
        left, right = 150, 850
        bottom, top = 250, 650

        while attempt < max_attempts and not found:
            cx = random.randint(left, right)
            cy = random.randint(bottom, top)
            if self._is_position_free(cx, cy):
                self.x, self.y = cx, cy
                found = True
            attempt += 1

        if not found:
            # 위치를 못 찾았을 경우 기본값 (중앙 근처)
            self.x, self.y = 500, 450

    def _is_position_free(self, x, y):
        # Host의 충돌 박스 크기 예상 (35, 75)
        la, ba, ra, ta = x - 35, y - 75, x + 35, y

        # 1. 게임 월드에 등록된 객체들(돌, 똥, 벽 등)과 충돌 검사
        for layer in game_world.world:
            for o in layer:
                if o is self: continue  # 자기 자신은 제외

                # get_bb가 있는 객체만 검사
                if hasattr(o, 'get_bb'):
                    try:
                        lb, bb, rb, tb = o.get_bb()
                    except Exception:
                        continue

                    # 겹치는지 확인 (AABB 충돌 검사)
                    if not (la > rb or ra < lb or ta < bb or ba > tb):
                        return False  # 겹침 -> 위치 사용 불가

        # 2. 아직 월드에 등록 안 됐지만 생성 예정인 다른 Host들과 충돌 검사
        for h in Host._instances:
            if h is self: continue
            # 좌표가 설정되지 않은 Host는 패스
            if not hasattr(h, 'x') or not hasattr(h, 'y'): continue

            try:
                hl, hb, hr, ht = h.get_bb()
            except Exception:
                continue

            if not (la > hr or ra < hl or ta < hb or ba > ht):
                return False

        return True

    @classmethod
    def spawn_many(cls, count, depth=1):
        """Host 인스턴스 여러개 생성하여 game_world에 추가하고 충돌 페어를 등록한다."""
        spawned = []
        for _ in range(count):
            h = cls()
            game_world.add_object(h, depth)
            # 충돌 페어 등록: Isaac(후에 등록된 a/b 관례에 맞춰 play_mode와 중복 주의)
            game_world.add_collision_pair('isaac:host', None, h)
            game_world.add_collision_pair('host:tear', h, None)
            spawned.append(h)
        return spawned

    def destroy(self):
        """game_world에서 안전하게 제거하고 내부 리스트에서 자신을 제거."""
        try:
            game_world.remove_object(self)
        except Exception:
            pass
        try:
            Host._instances.remove(self)
        except ValueError:
            pass

    def get_bb(self):
        return self.x - 35, self.y - 75, self.x + 35, self.y

    def _find_isaac(self):
        for layer in game_world.world:
            for o in layer:
                if o.__class__.__name__ == 'Isaac':
                    return o
        return None

    def update(self):
        dt = game_framework.frame_time

        # 사망 처리
        if self.hp <= 0:
            if random.random() < 0.5:  # 50% 확률
                coin = Coin(self.x, self.y)
                game_world.add_object(coin, 1)
                game_world.add_collision_pair('isaac:coin', None, coin)
                if common.stage and hasattr(common.stage, 'coins'):
                    common.stage.coins.append(coin)
            self.destroy()
            return

        # 쿨다운 감소
        if self._cooldown_timer > 0.0:
            self._cooldown_timer = max(0.0, self._cooldown_timer - dt)

        # 상태 머신(간단화된 기존 로직 유지)
        if self.state == 'idle':
            self.is_vulnerable = False
            isaac = self._find_isaac()
            if isaac and self._cooldown_timer == 0.0:
                if abs(self.x - isaac.x) <= self.align_tolerance and abs(self.y - isaac.y) <= self.detect_range:
                    self._start_attack()
                elif abs(self.y - isaac.y) <= self.align_tolerance and abs(self.x - isaac.x) <= self.detect_range:
                    self._start_attack()

        elif self.state == 'attack':
            self._attack_timer -= dt
            self._shoot_timer -= dt
            self._attack_anim_timer += dt
            while True:
                cur_dur = self.attack_frame_durations[self.attack_frame_index]
                if self._attack_anim_timer < cur_dur:
                    break
                self._attack_anim_timer -= cur_dur
                prev_index = self.attack_frame_index
                self.attack_frame_index = (self.attack_frame_index + 1) % self.attack_frames
                if not self._has_shot and not self._pending_shot and self.attack_frame_index == 1:
                    self._pending_shot = True
                    self._fire_delay_timer = self.fire_delay

            if self._pending_shot and not self._has_shot:
                self._fire_delay_timer -= dt
                if self._fire_delay_timer <= 0.0 and self._attack_timer > 0.0:
                    isaac = self._find_isaac()
                    if isaac:
                        bullet = HostBullet(self.x, self.y, isaac.x, isaac.y)
                    else:
                        bullet = HostBullet(self.x, self.y, self.x, self.y - 1)
                    game_world.add_object(bullet, 1)
                    # HostBullet은 자체적으로 충돌 검사(수동)하므로 여기서는 충돌 페어 등록 생략
                    self._has_shot = True
                    self._pending_shot = False

            if self._attack_timer <= 0.0:
                self.state = 'idle'
                self.is_vulnerable = False
                self._cooldown_timer = self.attack_cooldown
                self._pending_shot = False
                self._fire_delay_timer = 0.0

        # 애니메이션 프레임 갱신
        dtf = game_framework.frame_time
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * dtf) % FRAMES_PER_ACTION

    def _start_attack(self):
        self.state = 'attack'
        self._attack_timer = self.attack_duration
        self._shoot_timer = 0.0
        self.is_vulnerable = True
        self._has_shot = False

        self.attack_frame_index = 0
        self._attack_anim_timer = 0.0

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Host.image:
            if self.state == 'attack':
                fx = int(self.attack_frame_index) * 32
                Host.image.clip_draw(fx, 0, 32, 60, sx, sy, 70, 150)
                l, b, r, t = self.get_bb()
                ls, bs = game_world.world_to_screen(l, b)
                rs, ts = game_world.world_to_screen(r, t)
                draw_rectangle(ls, bs, rs, ts)

            else:
                Host.image.clip_draw(0, 0, 32, 60, sx, sy, 70, 150)
        else:
            draw_rectangle(sx - 35, sy - 75, sx + 35, sy)

    def handle_collision(self, group, other):
        # 가만히(idle)일 때 무적, 공격 중일 때만 피해 허용
        if group == 'host:tear' or group == 'host_bullet:isaac':
            if self.is_vulnerable:
                damage = getattr(other, 'damage', 1)
                self.hp -= damage



class HostBullet:
    image = None

    def __init__(self, x, y, tx, ty):
        try:
            if HostBullet.image is None:
                HostBullet.image = load_image("resource/monster/HostBullet.png")
        except Exception:
            HostBullet.image = None
        self.x = x
        self.y = y
        self.speed = 320.0
        dx = tx - x
        dy = ty - y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist == 0:
            self.vx, self.vy = 0.0, -1.0
        else:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        self.life = 3.0
        self.owner = 'host'

    def destroy(self):
        try:
            game_world.remove_object(self)
        except Exception:
            pass

    def get_bb(self):
        return self.x - 10, self.y - 10, self.x + 10, self.y + 10

    def update(self):
        dt = game_framework.frame_time
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0:
            self.destroy()
            return

        # 플레이어 충돌 검사
        isaac = None
        for layer in game_world.world:
            for o in layer:
                if o.__class__.__name__ == 'Isaac':
                    isaac = o
                    break
            if isaac:
                break

        if isaac:
            la, ba, ra, ta = self.get_bb()
            lb, bb, rb, tb = isaac.get_bb()
            if not (la > rb or ra < lb or ta < bb or ba > tb):
                isaac.handle_collision('host_bullet:isaac', self)
                self.destroy()

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if HostBullet.image:
            HostBullet.image.draw(sx, sy)
        la, ba, ra, ta = self.get_bb()
        ls, bs = game_world.world_to_screen(la, ba)
        rs, ts = game_world.world_to_screen(ra, ta)
        draw_rectangle(ls, bs, rs, ts)