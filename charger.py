from pico2d import *
import game_world
import random
import game_framework
import common
from coin import Coin
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector


PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

WANDER_SPEED_PPS = RUN_SPEED_PPS * 0.7
CHARGE_SPEED_PPS = RUN_SPEED_PPS * 1.5  # 돌진 속도

# 상태 상수
STATE_WANDER = 0
STATE_CHARGE = 1

ALIGN_TOL = 32  # 축 정렬 허용 범위


class Charger:
    image = None
    _instances = []

    spawn_points = [
        (1000.0, 500.0), (1000.0, 450.0), (800.0, 500.0), (850.0, 450.0),
        (900,500) , (950,500), (980,500)
    ]

    def __init__(self):
        if Charger.image is None:
            try:
                Charger.image = load_image("resource/monster/Charger.png")
            except Exception:
                Charger.image = None

        self.size_x = 20
        self.size_y = 25
        self.dead_s = load_wav('resource/sound/monster_dead.mp3')
        self.dead_s.set_volume(5)
        self.attack_s = load_wav('resource/sound/charger_attack.mp3')
        self.attack_s.set_volume(5)

        self._init_position()
        Charger._instances.append(self)

        self.frame = 0.0
        self.hp = 3
        self.state = STATE_WANDER
        self.dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        self.normal_frames = 4.0

        # BT용 변수
        self.wander_timer = 0
        self.charge_dir = (0, 0)
        self.tx, self.ty = 0, 0

        self.build_behavior_tree()

    def _init_position(self):
        candidates = list(Charger.spawn_points)
        random.shuffle(candidates)

        # 2. 후보 좌표들을 순회하며 다른 Charger와 겹치지 않는 곳을 찾음
        for px, py in candidates:
            if not self._is_overlapping_with_other_charger(px, py):
                self.x, self.y = px, py
                return  # 성공하면 종료

        # 3. 만약 모든 자리에 다른 Charger가 있다면, 그냥 첫 번째 후보지에 겹쳐서라도 스폰
        self.x, self.y = candidates[0]

        # [새로 추가] 다른 Charger와 겹치는지 확인하는 함수

    def _is_overlapping_with_other_charger(self, x, y):
        la, ba, ra, ta = x - self.size_x, y - self.size_y, x + self.size_x, y + self.size_y

        for other in Charger._instances:
            # 이미 생성된 Charger들의 충돌박스와 비교
            if not hasattr(other, 'get_bb'): continue

            l, b, r, t = other.get_bb()

            # AABB 충돌 검사
            if not (la > r or ra < l or ta < b or ba > t):
                return True  # 겹침

        return False  # 안 겹침
    def _find_stage_bounds(self):
        if common.stage and hasattr(common.stage, 'get_map_bounds'):
            return common.stage.get_map_bounds()
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
                if o.__class__.__name__ == 'Sucker': continue
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

    # --- Behavior Tree 노드 함수들 ---

    def is_aligned_with_isaac(self):
        target = common.isaac
        if not target: return BehaviorTree.FAIL

        dx = abs(self.x - target.x)
        dy = abs(self.y - target.y)

        # Y축 정렬 (수평 돌진)
        if dy < ALIGN_TOL:
            if self._can_see_target(target, 'x'):
                self.charge_dir = (1, 0) if target.x > self.x else (-1, 0)
                self.dir = self.charge_dir  # 방향 즉시 업데이트 (그리기용)
                return BehaviorTree.SUCCESS

        # X축 정렬 (수직 돌진)
        elif dx < ALIGN_TOL:
            if self._can_see_target(target, 'y'):
                self.charge_dir = (0, 1) if target.y > self.y else (0, -1)
                self.dir = self.charge_dir  # 방향 즉시 업데이트 (그리기용)
                return BehaviorTree.SUCCESS

        return BehaviorTree.FAIL

    def do_charge(self):
        self.state = STATE_CHARGE

        delta = game_framework.frame_time

        # 1. 이동 계산
        next_x = self.x + self.charge_dir[0] * CHARGE_SPEED_PPS * delta
        next_y = self.y + self.charge_dir[1] * CHARGE_SPEED_PPS * delta

        # 2. 벽 충돌 검사 -> 충돌 시 FAIL 반환 (배회로 전환)
        if not self._is_position_safe(next_x, next_y):
            self.state = STATE_WANDER  # 상태 복귀
            self.timer = 1.0  # 잠시 멈춤 효과
            return BehaviorTree.FAIL

        # 3. Isaac이 공격 경로(범위) 내에 있는지 확인 (회피 구현)
        target = common.isaac
        keep_charging = False

        if target:
            dx = abs(self.x - target.x)
            dy = abs(self.y - target.y)

            # 수평 이동 중일 때
            if self.charge_dir[0] != 0:
                self.attack_s.play(1)
                if dy < ALIGN_TOL:  # 여전히 Y축 정렬 상태여야 함
                    if (self.charge_dir[0] > 0 and target.x > self.x) or \
                            (self.charge_dir[0] < 0 and target.x < self.x):
                        keep_charging = True

            # 수직 이동 중일 때
            elif self.charge_dir[1] != 0:
                self.attack_s.play(1)
                if dx < ALIGN_TOL:  # 여전히 X축 정렬 상태여야 함
                    if (self.charge_dir[1] > 0 and target.y > self.y) or \
                            (self.charge_dir[1] < 0 and target.y < self.y):
                        keep_charging = True

        # 조건 불만족(Isaac이 피함) 시 돌진 중단 -> FAIL 반환
        if not keep_charging:
            self.state = STATE_WANDER
            self.timer = 0.5
            return BehaviorTree.FAIL

        # 모든 조건 통과 시 이동 적용 및 RUNNING 반환
        self.x, self.y = next_x, next_y
        return BehaviorTree.RUNNING

    def do_wander(self):

        self.state = STATE_WANDER

        delta = game_framework.frame_time

        # 타이머 처리
        self.wander_timer -= delta
        if self.wander_timer <= 0:
            self._choose_random_direction()
            self.wander_timer = random.uniform(1.0, 3.0)

        next_x = self.x + self.dir[0] * WANDER_SPEED_PPS * delta
        next_y = self.y + self.dir[1] * WANDER_SPEED_PPS * delta

        if self._is_position_safe(next_x, next_y):
            self.x, self.y = next_x, next_y
        else:
            self._choose_random_direction()

        return BehaviorTree.SUCCESS

    def _choose_random_direction(self):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(dirs)
        for d in dirs:
            dx, dy = d
            if self._is_position_safe(self.x + dx * 10, self.y + dy * 10):
                self.dir = d
                self.wander_timer = random.uniform(1.0, 3.0)  # 방향 전환 후 타이머 리셋
                return
        self.dir = (0, 0)

    def build_behavior_tree(self):
        # 1. 공격 시퀀스: 정렬됨? -> 돌진
        c_aligned = Condition('Aligned?', self.is_aligned_with_isaac)
        a_charge = Action('Charge', self.do_charge)
        seq_attack = Sequence('Attack Sequence', c_aligned, a_charge)

        # 2. 배회 액션
        a_wander = Action('Wander', self.do_wander)

        # 3. 루트: 공격 시도 -> 안되면 배회
        root = Selector('Charger Logic', seq_attack, a_wander)

        self.bt = BehaviorTree(root)

    def update(self):
        # BT 실행
        self.bt.run()

        # 애니메이션 프레임 업데이트
        delta = game_framework.frame_time
        speed_factor = 2.0 if self.state == STATE_CHARGE else 1.0
        self.frame = (self.frame + self.normal_frames * speed_factor * delta)

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)

        if Charger.image is None:
            draw_rectangle(sx - self.size_x, sy - self.size_y, sx + self.size_x, sy + self.size_y)
            return

        dx, dy = self.dir


        if self.state == STATE_CHARGE:
            charge_frame_idx = 0  # 돌진 이미지는 프레임 0번 고정

            if dx > 0:  # [돌진] 오른쪽 (Right)
                Charger.image.clip_draw(charge_frame_idx * 32 + 32, 0, 32, 32, sx, sy, 64, 64)

            elif dx < 0:  # [돌진] 왼쪽 (Left)
                Charger.image.clip_composite_draw(charge_frame_idx * 32 + 32, 0, 32, 32, 0, 'h', sx, sy, 64, 64)

            elif dy > 0:  # [돌진] 위쪽 (Up)
                Charger.image.clip_draw(charge_frame_idx * 32 + 64, 0, 32, 32, sx, sy, 64, 64)

            else:  # [돌진] 아래쪽 (Down)
                Charger.image.clip_draw(charge_frame_idx * 32, 0, 32, 32, sx, sy, 64, 64)

        else:  # STATE_WANDER
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
            damage = getattr(other, 'damage', 1)  # 안전하게 가져오기
            self.hp -= damage
            if self.hp <= 0:
                if random.random() < 0.5:  # 50% 확률
                    coin = Coin(self.x, self.y)
                    game_world.add_object(coin, 1)
                    game_world.add_collision_pair('isaac:coin', None, coin)
                    if common.stage and hasattr(common.stage, 'coins'):
                        common.stage.coins.append(coin)
                self.destroy()

    def destroy(self):
        game_world.remove_object(self)
        self.dead_s.play(1)
        if self in Charger._instances:
            Charger._instances.remove(self)