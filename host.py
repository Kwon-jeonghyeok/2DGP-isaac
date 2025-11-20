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
        if Host.image is None:
            try:
                Host.image = load_image("resource/monster/Host.png")
            except Exception:
                Host.image = None
        self.x, self.y = random.randint(180, 820), random.randint(200, 650)
        self.frame = 0.0
        self.hp = 3

        self.state = 'idle'
        # 감지/공격 파라미터
        self.align_tolerance = 24
        self.detect_range = 220
        self.attack_cooldown = 2.0
        self._cooldown_timer = 0.0

        self.attack_duration = 0.9
        self._attack_timer = 0.0
        self.shoot_interval = 0.25
        self._shoot_timer = 0.0

        self.is_vulnerable = False
        self._has_shot = False

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
            game_world.remove_object(self)
            return

        # 쿨다운 감소
        if self._cooldown_timer > 0.0:
            self._cooldown_timer = max(0.0, self._cooldown_timer - dt)

        # 상태 머신
        if self.state == 'idle':
            self.is_vulnerable = False
            isaac = self._find_isaac()
            if isaac and self._cooldown_timer == 0.0:
                # x축 혹은 y축 일직선 근접 검사
                if abs(self.x - isaac.x) <= self.align_tolerance and abs(self.y - isaac.y) <= self.detect_range:
                    self._start_attack()
                elif abs(self.y - isaac.y) <= self.align_tolerance and abs(self.x - isaac.x) <= self.detect_range:
                    self._start_attack()

        elif self.state == 'attack':
            # 공격 애니메이션 동안 취약하고 주기적으로 총알 발사
            self._attack_timer -= dt
            self._shoot_timer -= dt
            isaac = self._find_isaac()
            if not self._has_shot:
                # 첫 발만 발사
                self._has_shot = True
                if isaac:
                    bullet = HostBullet(self.x, self.y, isaac.x, isaac.y)
                else:
                    bullet = HostBullet(self.x, self.y, self.x, self.y - 1)
                game_world.add_object(bullet, 1)

            if self._attack_timer <= 0.0:
                self.state = 'idle'
                self.is_vulnerable = False
                self._cooldown_timer = self.attack_cooldown

        # 애니메이션 프레임 갱신
        dtf = game_framework.frame_time
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * dtf) % FRAMES_PER_ACTION

    def _start_attack(self):
        self.state = 'attack'
        self._attack_timer = self.attack_duration
        self._shoot_timer = 0.0
        self.is_vulnerable = True
        self._has_shot = False

    def draw(self):
        if Host.image:
            Host.image.clip_draw(0, 0, 32, 60, self.x, self.y, 70, 150)
        else:
            # 이미지가 없으면 단순 사각형으로 표시
            draw_rectangle(self.x - 35, self.y - 75, self.x + 35, self.y)
        draw_rectangle(*self.get_bb())

    def handle_collision(self, group, other):
        # 가만히(idle)일 때 무적, 공격 중일 때만 피해 허용
        if group == 'host:tear' or group == 'host_bullet:isaac':
            if self.is_vulnerable:
                self.hp -= 1


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
        self.speed = 300.0
        dx = tx - x
        dy = ty - y
        dist = (dx*dx + dy*dy) ** 0.5
        if dist == 0:
            self.vx, self.vy = 0.0, -1.0
        else:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        self.life = 3.0
        self.owner = 'host'

    def get_bb(self):
        return self.x - 8, self.y - 8, self.x + 8, self.y + 8

    def update(self):
        dt = game_framework.frame_time
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0:
            try:
                game_world.remove_object(self)
            except Exception:
                pass
            return

        # 플레이어 충돌 직접 검사 (game_world의 collide와 동일 로직)
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
                # 충돌 처리: Isaac에게 데미지 적용 (또는 handle_collision 호출)
                isaac.handle_collision('host_bullet:isaac', self)

                try:
                    game_world.remove_object(self)
                except Exception:
                    pass

    def draw(self):
        if HostBullet.image:
            HostBullet.image.draw(self.x, self.y)
        else:
            draw_rectangle(*self.get_bb())
