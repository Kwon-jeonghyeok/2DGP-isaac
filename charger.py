from pico2d import load_image, draw_rectangle
import game_world
import random
import math
import game_framework
import common

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

WANDER_SPEED_PPS = RUN_SPEED_PPS * 0.7
CHARGE_SPEED_PPS = RUN_SPEED_PPS * 1.5  # 돌진 속도

STATE_WANDER = 0
STATE_CHARGE = 1

ALIGN_TOL = 32  # 축 정렬 허용 범위 (이 범위를 벗어나면 Isaac이 피한 것으로 간주)


class Charger:
    image = None
    _instances = []

    spawn_points = [
        (750.0, 500.0), (800.0, 400.0), (1200.0, 500.0), (1100.0, 400.0),
    ]

    def __init__(self):
        if Charger.image is None:
            try:
                Charger.image = load_image("resource/monster/Charger.png")
            except Exception:
                Charger.image = None

        self.size_x = 20
        self.size_y = 25

        self._init_position()

        Charger._instances.append(self)

        self.frame = 0.0
        self.hp = 3

        self.state = STATE_WANDER
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.timer = 0

        self.normal_frames = 4.0
        self.chase_frames = 1.0

    def _init_position(self):
        bounds = self._find_stage_bounds()
        if bounds:
            left, right = bounds.get('map_left', 100), bounds.get('map_right', 1475)
            bottom, top = bounds.get('map_bottom', 175), bounds.get('map_top', 700)
        else:
            left, right, bottom, top = 100, 1475, 175, 700

        cx, cy = (left + right) / 2.0, (bottom + top) / 2.0
        placed = False
        if Charger.spawn_points:
            for px, py in Charger.spawn_points:
                if self._point_free_for_spawn(px, py):
                    self.x, self.y = px, py
                    placed = True
                    break
        if not placed:
            self.x, self.y = float(cx), float(cy)

    def _point_free_for_spawn(self, px, py):
        if not self._is_position_safe(px, py):
            return False
        la, ba, ra, ta = px - self.size_x, py - self.size_y, px + self.size_x, py + self.size_y
        for s in Charger._instances:
            if s is self: continue
            sl, sb, sr, st = s.get_bb()
            if not (la > sr or ra < sl or ta < sb or ba > st):
                return False
        return True

    def _find_stage_bounds(self):
        for layer in game_world.world:
            for o in layer:
                if hasattr(o, 'get_map_bounds'):
                    return o.get_map_bounds()
        return None

    def get_bb(self):
        return (self.x - self.size_x, self.y - self.size_y,
                self.x + self.size_x, self.y + self.size_y)

    def _is_position_safe(self, x, y):
        la, ba, ra, ta = x - self.size_x, y - self.size_y, x + self.size_x, y + self.size_y
        bounds = self._find_stage_bounds()
        if bounds:
            if la < bounds['map_left'] or ra > bounds['map_right'] or ba < bounds['map_bottom'] or ta > bounds[
                'map_top']:
                return False

        for layer in game_world.world:
            for o in layer:
                if o is self or o is common.isaac: continue
                if not hasattr(o, 'get_bb'): continue
                lb, bb, rb, tb = o.get_bb()
                if not (la > rb or ra < lb or ta < bb or ba > tb):
                    return False
        return True

    def _can_see_target(self, target, axis):
        if not target: return False
        if axis == 'x':
            min_x, max_x = min(self.x, target.x), max(self.x, target.x)
            min_y, max_y = self.y - self.size_y + 5, self.y + self.size_y - 5
            check_l, check_b, check_r, check_t = min_x, min_y, max_x, max_y
        else:
            min_y, max_y = min(self.y, target.y), max(self.y, target.y)
            min_x, max_x = self.x - self.size_x + 5, self.x + self.size_x - 5
            check_l, check_b, check_r, check_t = min_x, min_y, max_x, max_y

        for layer in game_world.world:
            for o in layer:
                if o is self or o is target: continue
                if not hasattr(o, 'get_bb'): continue
                lb, bb, rb, tb = o.get_bb()
                if not (check_l > rb or check_r < lb or check_t < bb or check_b > tb):
                    return False
        return True

    def update(self):
        delta = game_framework.frame_time
        speed_factor = 2.0 if self.state == STATE_CHARGE else 1.0
        self.frame = (self.frame + self.normal_frames * speed_factor * delta)

        if self.state == STATE_WANDER:
            self._update_wander(delta)
        elif self.state == STATE_CHARGE:
            self._update_charge(delta)

    def _update_wander(self, delta):
        target = common.isaac
        if target:
            dx = abs(self.x - target.x)
            dy = abs(self.y - target.y)

            # 플레이어 발견 시 돌진 상태로 전환
            if dy < ALIGN_TOL:
                if self._can_see_target(target, 'x'):
                    self.state = STATE_CHARGE
                    self.dir = (1, 0) if target.x > self.x else (-1, 0)
                    return

            elif dx < ALIGN_TOL:
                if self._can_see_target(target, 'y'):
                    self.state = STATE_CHARGE
                    self.dir = (0, 1) if target.y > self.y else (0, -1)
                    return

        self.timer -= delta
        if self.timer <= 0:
            self._choose_random_direction()
            self.timer = random.uniform(1.0, 3.0)

        next_x = self.x + self.dir[0] * WANDER_SPEED_PPS * delta
        next_y = self.y + self.dir[1] * WANDER_SPEED_PPS * delta

        if self._is_position_safe(next_x, next_y):
            self.x, self.y = next_x, next_y
        else:
            self._choose_random_direction()

    def _update_charge(self, delta):
        # 1. 이동 계산
        next_x = self.x + self.dir[0] * CHARGE_SPEED_PPS * delta
        next_y = self.y + self.dir[1] * CHARGE_SPEED_PPS * delta

        # 2. 벽 충돌 검사
        if not self._is_position_safe(next_x, next_y):
            self.state = STATE_WANDER
            self.timer = 1.0
            return

        # 3.  Isaac이공격 경로(범위) 내에 있는지 확인
        target = common.isaac
        keep_charging = False

        if target:
            dx = abs(self.x - target.x)
            dy = abs(self.y - target.y)

            # 수평 이동 중일 때 (X축 돌진)
            if self.dir[0] != 0:
                # Isaac이 Y축 범위 내에 있고(피하지 않음) + 진행 방향 쪽에 있어야 함
                if dy < ALIGN_TOL:
                    # 오른쪽으로 가는데 target이 오른쪽에 있거나, 왼쪽으로 가는데 target이 왼쪽에 있어야 함
                    if (self.dir[0] > 0 and target.x > self.x) or \
                            (self.dir[0] < 0 and target.x < self.x):
                        keep_charging = True

            # 수직 이동 중일 때 (Y축 돌진)
            elif self.dir[1] != 0:
                if dx < ALIGN_TOL:
                    if (self.dir[1] > 0 and target.y > self.y) or \
                            (self.dir[1] < 0 and target.y < self.y):
                        keep_charging = True

        # 조건 불만족(회피했거나 지나침)시 돌진 중단
        if not keep_charging:
            self.state = STATE_WANDER
            self.timer = 0.5  # 잠깐 대기 후 다시 배회
            return

        # 모든 조건 통과 시 이동 적용
        self.x, self.y = next_x, next_y

    def _choose_random_direction(self):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(dirs)
        for d in dirs:
            dx, dy = d
            if self._is_position_safe(self.x + dx * 10, self.y + dy * 10):
                self.dir = d
                return
        self.dir = (0, 0)

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)

        if Charger.image is None:
            draw_rectangle(sx - self.size_x, sy - self.size_y, sx + self.size_x, sy + self.size_y)
            return

        dx, dy = self.dir

        if self.state == STATE_CHARGE:
            charge_frame_idx = 0

            if dx > 0:  # [돌진] 오른쪽 (Right)
                Charger.image.clip_draw(charge_frame_idx * 32 +32, 0, 32, 32, sx, sy, 64, 64)

            elif dx < 0:  # [돌진] 왼쪽 (Left)
                Charger.image.clip_composite_draw(charge_frame_idx * 32+32, 0, 32, 32, 0, 'h', sx, sy, 64, 64)

            elif dy > 0:  # [돌진] 위쪽 (Up)
                Charger.image.clip_draw(charge_frame_idx * 32+64, 0, 32, 32, sx, sy, 64, 64)

            else:  # [돌진] 아래쪽 (Down)
                Charger.image.clip_draw(charge_frame_idx * 32, 0, 32, 32, sx, sy, 64, 64)

        else:
            walk_frame_idx = int(self.frame) % 4

            if dx > 0:  # [걷기] 오른쪽 (Right)
                Charger.image.clip_draw(walk_frame_idx * 32, 96, 32, 32, sx, sy, 64, 64)

            elif dx < 0:  # [걷기] 왼쪽 (Left)
                Charger.image.clip_composite_draw(walk_frame_idx * 32, 96, 32, 32, 0, 'h', sx, sy, 64, 64)

            elif dy > 0:  # [걷기] 위쪽 (Up)
                Charger.image.clip_draw(walk_frame_idx * 32, 64, 32, 32, sx, sy, 64, 64)

            else:  # [걷기] 아래쪽 (Down)
                Charger.image.clip_draw(walk_frame_idx * 32, 32, 32, 32, sx, sy, 64, 64)

    def handle_collision(self, group, other):
        if group == 'charger:tear':
            self.hp -= 1
            if self.hp <= 0:
                self.destroy()

    def destroy(self):
        game_world.remove_object(self)
        if self in Charger._instances:
            Charger._instances.remove(self)