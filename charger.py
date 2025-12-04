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

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

ALIGN_TOL = 48

class Charger:
    image = None
    _instances = []

    spawn_points = [
        (750.0, 500.0),
        (800.0, 400.0),
        (1200.0, 500.0),
        (1100.0, 400.0),
    ]

    def __init__(self):
        if Charger.image is None:
            try:
                Charger.image = load_image("resource/monster/Charger.png")
            except Exception:
                Charger.image = None

        self.size_x = 20
        self.size_y = 25

        bounds = self._find_stage_bounds()
        if bounds:
            left = bounds.get('map_left', 100)
            right = bounds.get('map_right', 1475)
            bottom = bounds.get('map_bottom', 175)
            top = bounds.get('map_top', 700)
        else:
            left, right, bottom, top = 100, 1475, 175, 700

        cx = (left + right) / 2.0
        cy = (bottom + top) / 2.0

        placed = False

        # 1) 파일 내부에 정의한 spawn_points
        if Charger.spawn_points:
            for px, py in Charger.spawn_points:
                try:
                    px = float(px); py = float(py)
                except Exception:
                    continue
                if self._point_free_for_spawn(px, py):
                    self.x, self.y = px, py
                    placed = True
                    break

        # 실패하면 중앙 배치
        if not placed:
            self.x, self.y = float(cx), float(cy)

        Charger._instances.append(self)

        self.frame = 0.0
        self.hp = 3
        self.mode_chase = False
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.speed = RUN_SPEED_PPS
        self.normal_frames = 4.0
        self.chase_frames = 1.0
        self.current_frames = self.normal_frames

    def _point_free_for_spawn(self, px, py):
        # 월드 객체와 충돌 없는지, 기존 Charger들과 겹치지 않는지 검사
        if not self._is_position_free(px, py):
            return False
        la, ba, ra, ta = px - self.size_x, py - self.size_y, px + self.size_x, py + self.size_y
        for s in Charger._instances:
            try:
                sl, sb, sr, st = s.get_bb()
            except Exception:
                continue
            if not (la > sr or ra < sl or ta < sb or ba > st):
                return False
        return True

    def _find_stage_bounds(self):
        for layer in game_world.world:
            for o in layer:
                if hasattr(o, 'get_map_bounds'):
                    try:
                        return o.get_map_bounds()
                    except Exception:
                        continue
        return None

    def get_bb(self):
        return (self.x - self.size_x, self.y - self.size_y,
                self.x + self.size_x, self.y + self.size_y)

    def _is_position_free(self, x, y):
        la, ba, ra, ta = x - self.size_x, y - self.size_y, x + self.size_x, y + self.size_y
        for layer in game_world.world:
            for o in layer:
                if not hasattr(o, 'get_bb'):
                    continue
                try:
                    lb, bb, rb, tb = o.get_bb()
                except Exception:
                    continue
                if not (la > rb or ra < lb or ta < bb or ba > tb):
                    return False
        for s in Charger._instances:
            if s is self:
                continue
            try:
                sl, sb, sr, st = s.get_bb()
            except Exception:
                continue
            if not (la > sr or ra < sl or ta < sb or ba > st):
                return False
        return True

    def _would_collide(self, x, y):
        la, ba, ra, ta = x - self.size_x, y - self.size_y, x + self.size_x, y + self.size_y
        bounds = self._find_stage_bounds()
        if bounds:
            if la < bounds['map_left'] or ra > bounds['map_right'] or ba < bounds['map_bottom'] or ta > bounds['map_top']:
                return True
        for layer in game_world.world:
            for o in layer:
                if o is self:
                    continue
                if not hasattr(o, 'get_bb'):
                    continue
                try:
                    lb, bb, rb, tb = o.get_bb()
                except Exception:
                    continue
                if not (la > rb or ra < lb or ta < bb or ba > tb):
                    if o is common.isaac:
                        continue
                    return True
        for s in Charger._instances:
            if s is self:
                continue
            try:
                sl, sb, sr, st = s.get_bb()
            except Exception:
                continue
            if not (la > sr or ra < sl or ta < sb or ba > st):
                return True
        return False

    def _is_path_clear_axis(self, axis, band=None):
        if common.isaac is None:
            return False
        if axis not in ('x', 'y'):
            return False
        if band is None:
            band = max(self.size_x, self.size_y) * 3

        if axis == 'x':
            sx = min(self.x, common.isaac.x)
            ex = max(self.x, common.isaac.x)
            y_min = self.y - band
            y_max = self.y + band
            for layer in game_world.world:
                for o in layer:
                    if not hasattr(o, 'get_bb') or o is self or o is common.isaac:
                        continue
                    try:
                        lb, bb, rb, tb = o.get_bb()
                    except Exception:
                        continue
                    if rb >= sx and lb <= ex and not (tb < y_min or bb > y_max):
                        return False
            return True
        else:
            sy = min(self.y, common.isaac.y)
            ey = max(self.y, common.isaac.y)
            x_min = self.x - band
            x_max = self.x + band
            for layer in game_world.world:
                for o in layer:
                    if not hasattr(o, 'get_bb') or o is self or o is common.isaac:
                        continue
                    try:
                        lb, bb, rb, tb = o.get_bb()
                    except Exception:
                        continue
                    if tb >= sy and bb <= ey and not (rb < x_min or lb > x_max):
                        return False
            return True

    def update(self):
        delta = game_framework.frame_time
        self.mode_chase = False
        if common.isaac is not None:
            if abs(self.x - common.isaac.x) < ALIGN_TOL:
                if self._is_path_clear_axis('y', band=max(80, self.size_x * 4)):
                    self.mode_chase = True
                    sign = 1 if common.isaac.y > self.y else -1
                    self.dir = (0, sign)
            elif abs(self.y - common.isaac.y) < ALIGN_TOL:
                if self._is_path_clear_axis('x', band=max(80, self.size_y * 4)):
                    self.mode_chase = True
                    sign = 1 if common.isaac.x > self.x else -1
                    self.dir = (sign, 0)

        self.current_frames = self.chase_frames if self.mode_chase else self.normal_frames
        frames_to_advance = self.current_frames * ACTION_PER_TIME * delta
        self.frame = (self.frame + frames_to_advance) % max(1.0, self.current_frames)

        dx, dy = self.dir
        move_dist = self.speed * delta
        new_x = self.x + dx * move_dist
        new_y = self.y + dy * move_dist

        if self._would_collide(new_x, new_y):
            self._choose_random_direction()
        else:
            self.x, self.y = new_x, new_y

    def _choose_random_direction(self):
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        random.shuffle(dirs)
        for d in dirs:
            dx, dy = d
            test_x = self.x + dx * (self.size_x + 5)
            test_y = self.y + dy * (self.size_y + 5)
            if not self._would_collide(test_x, test_y):
                self.dir = d
                return
        self.dir = (0,0)

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Charger.image:
            flip = False
            if self.dir[0] < 0:
                flip = True
            frame_idx = int(self.frame) % max(1, int(self.current_frames))
            try:
                if flip:
                    Charger.image.clip_composite_draw(frame_idx * 32, 0, 32, 32, 0, 'h', sx, sy, 64, 64)
                else:
                    Charger.image.clip_draw(frame_idx * 32, 0, 32, 32, sx, sy, 64, 64)
            except Exception:
                draw_rectangle(sx - self.size_x, sy - self.size_y, sx + self.size_x, sy + self.size_y)
        else:
            draw_rectangle(sx - self.size_x, sy - self.size_y, sx + self.size_x, sy + self.size_y)

    def handle_collision(self, group, other):
        if group == 'charger:tear':
            try:
                self.hp -= 1
            except Exception:
                pass
            if self.hp <= 0:
                self.destroy()

    def destroy(self):
        try:
            game_world.remove_object(self)
        except Exception:
            pass
        try:
            Charger._instances.remove(self)
        except ValueError:
            pass
