# python
# File: `sucker.py`
from pico2d import load_image, draw_rectangle
import game_world
import random

class Sucker:
    image = None
    _instances = []

    def __init__(self):
        if Sucker.image is None:
            try:
                Sucker.image = load_image("resource/monster/Sucker.png")
            except Exception:
                Sucker.image = None

        bounds = self._find_stage_bounds()
        if bounds:
            left = bounds.get('map_left', 100)
            right = bounds.get('map_right', 1500)
            bottom = bounds.get('map_bottom', 175)
            top = bounds.get('map_top', 700)
        else:
            left, right, bottom, top = 100, 900, 175, 700

        max_attempts = 200
        attempt = 0
        found = False
        last_x, last_y = (left + right) // 2, (bottom + top) // 2

        while attempt < max_attempts and not found:
            cx = random.randint(int(left + 40), int(right - 40))
            cy = random.randint(int(bottom + 40), int(top - 40))
            last_x, last_y = cx, cy
            if self._is_position_free(cx, cy):
                self.x, self.y = cx, cy
                found = True
            attempt += 1

        if not found:
            self.x, self.y = last_x, last_y

        Sucker._instances.append(self)

        self.frame = 0.0
        self.hp = 2
        self.state = 'idle'

    @classmethod
    def spawn_many(cls, count, depth=1):
        """Sucker 인스턴스들을 생성해서 game_world에 추가하고 충돌페어를 등록하여 리스트로 반환한다."""
        spawned = []
        for _ in range(count):
            s = cls()
            game_world.add_object(s, depth)
            # isaac은 init 시 이미 왼쪽 리스트에 추가되어 있어 None, s 로 추가하는 방식 유지
            game_world.add_collision_pair('isaac:sucker', None, s)
            # Tear(아이작의 공격)을 검사하는 기존 그룹 재사용
            game_world.add_collision_pair('host:tear', s, None)
            spawned.append(s)
        return spawned

    def destroy(self):
        """game_world에서 제거하고 내부 추적 리스트에서 자신을 제거."""
        try:
            game_world.remove_object(self)
        except Exception:
            # 이미 제거된 경우 무시
            pass
        try:
            Sucker._instances.remove(self)
        except ValueError:
            pass

    def _find_stage_bounds(self):
        for layer in game_world.world:
            for o in layer:
                if hasattr(o, 'get_map_bounds'):
                    try:
                        return o.get_map_bounds()
                    except Exception:
                        continue
        return None

    def _is_position_free(self, x, y):
        la, ba, ra, ta = x - 20, y - 25, x + 20, y + 25

        # 1) 월드에 현재 추가된 오브젝트들과 충돌 검사
        for layer in game_world.world:
            for o in layer:
                if not hasattr(o, 'get_bb'):
                    continue
                # 자신은 아직 월드에 없으므로 검사할 필요 없음
                try:
                    lb, bb, rb, tb = o.get_bb()
                except Exception:
                    continue
                if not (la > rb or ra < lb or ta < bb or ba > tb):
                    return False

        # 2) 이미 생성된 다른 Sucker들과 충돌 검사
        for s in Sucker._instances:
            if s is self:
                continue
            try:
                sl, sb, sr, st = s.get_bb()
            except Exception:
                continue
            if not (la > sr or ra < sl or ta < sb or ba > st):
                return False

        return True

    def get_bb(self):
        return self.x - 20, self.y - 25, self.x + 20, self.y + 25

    def update(self):
        pass

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Sucker.image:
            Sucker.image.draw(sx, sy)
        else:
            draw_rectangle(sx - 20, sy - 25, sx + 20, sy + 25)

        l, b, r, t = self.get_bb()
        ls, bs = game_world.world_to_screen(l, b)
        rs, ts = game_world.world_to_screen(r, t)
        draw_rectangle(ls, bs, rs, ts)

    def handle_collision(self, group, other):
        # isaac의 충돌 그룹명, 또는 host의 tear 그룹에 맞을 때 피해 처리
        if group == 'isaac:sucker' or group == 'host:tear':
            try:
                self.hp -= 1
            except Exception:
                pass
            if self.hp <= 0:
                self.destroy()
