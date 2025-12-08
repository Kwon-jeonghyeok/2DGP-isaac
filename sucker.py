from pico2d import load_image, draw_rectangle
import game_world
import random
import math
import game_framework
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
import common
from coin import Coin
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 2.0

animation_names = ['Fly', 'Idle']


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
        self.speed =0.0
        self.dir = 0.0

        self.patrol_center = (self.x, self.y)
        self.patrol_range = random.randint(40, 160)  # 각자 다른 범위
        self._patrol_dir = 1  # 1: 오른쪽으로 다음, -1: 왼쪽으로 다음

        self.tx, self.ty = 0, 0
        self.build_behavior_tree()

    """
    @classmethod
    def spawn_many(cls, count, depth=1):
        #Sucker 인스턴스들을 생성해서 game_world에 추가하고 충돌페어를 등록하여 리스트로 반환한다.
        spawned = []
        for _ in range(count):
            s = cls()
            game_world.add_object(s, depth)
            # isaac은 init 시 이미 왼쪽 리스트에 추가되어 있어 None, s 로 추가하는 방식 유지
            game_world.add_collision_pair('isaac:sucker', None, s)
            # Tear(아이작의 공격)을 검사하는 기존 그룹 재사용
            game_world.add_collision_pair('sucker:tear', s, None)
            spawned.append(s)
        return spawned
        """

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
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        try:
            self.bt.run()
        except Exception:
            pass

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Sucker.image:
            if math.cos(self.dir) < 0:
                Sucker.image.clip_composite_draw(int(self.frame) * 32, 0, 32, 32, 0, 'h', sx, sy, 64, 64)
            else:
                Sucker.image.clip_draw(int(self.frame) * 32, 0, 32, 32, sx, sy, 64, 64)
        else:
            draw_rectangle(sx - 20, sy - 25, sx + 20, sy + 25)

        l, b, r, t = self.get_bb()
        ls, bs = game_world.world_to_screen(l, b)
        rs, ts = game_world.world_to_screen(r, t)
        draw_rectangle(ls, bs, rs, ts)

    def handle_collision(self, group, other):
        if group == 'sucker:tear':
            try:
                damage = getattr(other, 'damage', 1)  # 안전하게 가져오기
                self.hp -= damage
            except Exception:
                pass
            if self.hp <= 0:
                if random.random() < 0.5:  # 50% 확률
                    coin = Coin(self.x, self.y)
                    game_world.add_object(coin, 1)
                    game_world.add_collision_pair('isaac:coin', None, coin)
                    if common.stage and hasattr(common.stage, 'coins'):
                        common.stage.coins.append(coin)
                self.destroy()

    def set_target_location(self, x=None, y=None):
        if not x or not y:
            raise ValueError('Location should be given')
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS

    def distance_less_than(self, x1, y1, x2, y2, r):
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 < (PIXEL_PER_METER*r) ** 2
    def move_little_to(self, tx, ty):
        self.dir = math.atan2(ty-self.y, tx-self.x)
        distance = RUN_SPEED_PPS * game_framework.frame_time
        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)
    def move_to(self, r=0.5):
        self.state = 'Fly'
        self.move_little_to(self.tx, self.ty)
        if self.distance_less_than(self.tx, self.ty, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING
    def if_isaac_nearby(self, r):
        if self.distance_less_than(common.isaac.x, common.isaac.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL
    def move_to_isaac(self, r=0.5):
        self.state = 'Fly'
        self.move_little_to(common.isaac.x, common.isaac.y)
        if self.distance_less_than(common.isaac.x, common.isaac.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING

    def get_patrol_location(self):
        cx, cy = self.patrol_center
        target_x = cx + self._patrol_dir * self.patrol_range
        # y는 중심 y로 고정(좌우 왕복)
        self.tx, self.ty = target_x, cy
        # 다음엔 반대 방향으로 이동
        self._patrol_dir *= -1
        return BehaviorTree.SUCCESS
        pass
    def build_behavior_tree(self):
        a1= Action('Move to', self.move_to)
        a2 = Action('Get Patrol Location', self.get_patrol_location)
        c1 = Condition('Isaac nearby?', self.if_isaac_nearby, 10)
        a3 = Action('Move to Isaac', self.move_to_isaac)
        root = chase_isaac = Sequence('Chase Isaac',c1 , a3)
        root = patrol = Sequence('Patrol', a2, a1)
        root = Selector('Sucker Behavior', chase_isaac, patrol)


        self.bt = BehaviorTree(root)