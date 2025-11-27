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
        max_attempts = 100
        attempt = 0
        found = False
        while attempt < max_attempts and not found:
            cx = random.randint(150, 900)
            cy = random.randint(275, 700)
            if self._is_position_free(cx, cy):
                self.x, self.y = cx, cy
                found = True
            attempt += 1
        if not found:
            # 실패 시 마지막 후보
            self.x, self.y = cx, cy
        self.frame = 0.0
        self.hp = 3

        self.state = 'idle'
        # 감지/공격 파라미터
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
        self.attack_frame_durations = [1.0, 2.0,1.0]

    def _is_position_free(self, x, y):
        la, ba, ra, ta = x - 35, y - 75, x + 35, y
        for layer in game_world.world:
            for o in layer:
                if hasattr(o, 'get_bb'):
                    try:
                        lb, bb, rb, tb = o.get_bb()
                    except Exception:
                        continue
                    if not (la > rb or ra < lb or ta < bb or ba > tb):
                        return False
        return True

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
            self._attack_timer -= dt
            self._shoot_timer -= dt
            self._attack_anim_timer += dt
            # 프레임별 지속시간을 사용해 전환 처리 (큰 dt로 여러 프레임을 건너뛰는 경우에도 처리)
            while True:
                cur_dur = self.attack_frame_durations[self.attack_frame_index]
                if self._attack_anim_timer < cur_dur:
                    break
                self._attack_anim_timer -= cur_dur
                # 한 스텝 전환
                prev_index = self.attack_frame_index
                self.attack_frame_index = (self.attack_frame_index + 1) % self.attack_frames
                # 새로 진입한 프레임이 1이면 발사 대기 시작
                if not self._has_shot and not self._pending_shot and self.attack_frame_index == 1:
                    self._pending_shot = True
                    self._fire_delay_timer = self.fire_delay
            # pending이면 지연 감소 후 발사
            if self._pending_shot and not self._has_shot:
                self._fire_delay_timer -= dt
                if self._fire_delay_timer <= 0.0 and self._attack_timer > 0.0:
                    isaac = self._find_isaac()
                    if isaac:
                        bullet = HostBullet(self.x, self.y, isaac.x, isaac.y)
                    else:
                        bullet = HostBullet(self.x, self.y, self.x, self.y - 1)
                    game_world.add_object(bullet, 1)
                    self._has_shot = True
                    self._pending_shot = False
            if self._attack_timer <= 0.0:
                self.state = 'idle'
                self.is_vulnerable = False
                self._cooldown_timer = self.attack_cooldown
                # 공격 종료 시 pending 취소
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
            else:
                Host.image.clip_draw(0, 0, 32, 60, sx, sy, 70, 150)
        else:
            draw_rectangle(sx - 35, sy - 75, sx + 35, sy)
        l, b, r, t = self.get_bb()
        ls, bs = game_world.world_to_screen(l, b)
        rs, ts = game_world.world_to_screen(r, t)
        draw_rectangle(ls, bs, rs, ts)

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
        self.speed = 320.0
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
        return self.x - 10, self.y - 10, self.x + 10, self.y + 10

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
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if HostBullet.image:
            HostBullet.image.draw(sx, sy)
        la, ba, ra, ta = self.get_bb()
        ls, bs = game_world.world_to_screen(la, ba)
        rs, ts = game_world.world_to_screen(ra, ta)
        draw_rectangle(ls, bs, rs, ts)
