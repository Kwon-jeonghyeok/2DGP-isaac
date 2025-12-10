from pico2d import *
import game_framework
import game_world
import common
import random
import math
from boss_bullet import BossBullet
from boss_laser import BossLaser

# =================================================================
# 보스 이미지 및 스프라이트 시트 설정
# =================================================================
FRAME_WIDTH = 100
FRAME_HEIGHT = 100
SHEET_HEIGHT = 500

# 행(Row)별 Y좌표 계산 (Pico2D는 Y좌표가 아래서부터 0, 100, 200...)
# Line 1 (Top)    : Y=400
# Line 2          : Y=300
# Line 3          : Y=200
# Line 4          : Y=100
# Line 5 (Bottom) : Y=0

Y_LINE_1 = SHEET_HEIGHT - FRAME_WIDTH * 1  # 400
Y_LINE_2 = SHEET_HEIGHT - FRAME_WIDTH * 2  # 300
Y_LINE_3 = SHEET_HEIGHT - FRAME_WIDTH * 3  # 200
Y_LINE_4 = SHEET_HEIGHT - FRAME_WIDTH * 4  # 100
Y_LINE_5 = SHEET_HEIGHT - FRAME_WIDTH * 5
# [기본 상태용]
ROW_PHASE1 = Y_LINE_1  # 1페이즈 얼굴 (Line 1)
ROW_PHASE2 = Y_LINE_2  # 2페이즈 해골 얼굴 (Line 3, 예시로 3번째 줄 사용)

# [변신 애니메이션 시퀀스 정의] (Y좌표, 프레임 인덱스 0부터 시작)
# 순서: 1행(4,5) -> 4행(1,2,3,4,5) -> 2행(1)
TRANSFORM_SEQUENCE = [
    (Y_LINE_1, 3),  # Line 1, Frame 4
    (Y_LINE_1, 4),  # Line 1, Frame 5
    (Y_LINE_4, 0),  # Line 4, Frame 1
    (Y_LINE_4, 1),  # Line 4, Frame 2
    (Y_LINE_4, 2),  # Line 4, Frame 3
    (Y_LINE_4, 3),  # Line 4, Frame 4
    (Y_LINE_4, 4),  # Line 4, Frame 5
    (Y_LINE_2, 0)  # Line 2, Frame 1
]
# 2. 5발 발사 (총 5프레임)
# 순서: 2줄(3,4,5) -> 3줄(1,2)
ATTACK_SPREAD_SEQ = [
    (Y_LINE_2, 2), (Y_LINE_2, 3), (Y_LINE_2, 4),
    (Y_LINE_3, 0), (Y_LINE_3, 1) # 마지막(인덱스 4)에 발사
]
# 3. 레이저 발사 (총 7프레임)
# 순서: 2줄(3,4,5) -> 3줄(1,2,3,4)
# 6,7번째 프레임(인덱스 5,6) 동안 레이저 활성화
ATTACK_LASER_SEQ = [
    (Y_LINE_2, 2), (Y_LINE_2, 3), (Y_LINE_2, 4),
    (Y_LINE_3, 0), (Y_LINE_3, 1),
    (Y_LINE_3, 2), (Y_LINE_3, 3)
]

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 3


def move_left_right_pattern(boss):
    # 이동
    boss.x += boss.dir_x * boss.speed * game_framework.frame_time

    # 벽 충돌 및 반전
    if common.stage and hasattr(common.stage, 'get_map_bounds'):
        bounds = common.stage.get_map_bounds()
        margin_x = boss.width / 2

        map_left = bounds.get('map_left', 0) + margin_x
        map_right = bounds.get('map_right', 1000) - margin_x

        if boss.x > map_right:
            boss.x = map_right
            boss.dir_x = -1
        elif boss.x < map_left:
            boss.x = map_left
            boss.dir_x = 1

# =================================================================
# [State 1] W 이동 상태 (1페이즈 기본)
# =================================================================
class MoveW:
    @staticmethod
    def enter(boss):
        boss.dir_y = -1
        if boss.dir_x == 0: boss.dir_x = 1
        boss.anim_row = ROW_PHASE1

    @staticmethod
    def exit(boss):
        pass

    @staticmethod
    def do(boss):
        boss.frame = (boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        boss.x += boss.dir_x * boss.speed * game_framework.frame_time
        boss.y += boss.dir_y * boss.speed * game_framework.frame_time
        handle_wall_bounce_w(boss)
        boss.attack_cooldown -= game_framework.frame_time

        # 잡몹 없으면 변신
        if len(boss.minions) == 0:
            boss.change_state(TransformMoveToCorner)
            return

        # 공격 패턴
        if boss.attack_cooldown <= 0 and len(boss.minions) > 0:
            boss.change_state(AttackThrow)

    @staticmethod
    def draw(boss):
        draw_boss_standard(boss)


# =================================================================
# [State 2] 잡몹 던지기 (1페이즈 패턴)
# =================================================================
class AttackThrow:
    @staticmethod
    def enter(boss):
        boss.timer = 5.0
        boss.anim_row = ROW_PHASE1
        for minion in boss.minions:
            if hasattr(minion, 'start_chase'): minion.start_chase()

    @staticmethod
    def exit(boss):
        boss.attack_cooldown = random.uniform(5.0, 8.0)
        for minion in boss.minions:
            if hasattr(minion, 'return_to_boss'): minion.return_to_boss()

    @staticmethod
    def do(boss):
        boss.frame = (boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        boss.x += boss.dir_x * boss.speed * game_framework.frame_time
        boss.y += boss.dir_y * boss.speed * game_framework.frame_time
        handle_wall_bounce_w(boss)

        if len(boss.minions) == 0:
            boss.change_state(TransformMoveToCorner)
            return

        boss.timer -= game_framework.frame_time
        if boss.timer <= 0:
            boss.change_state(MoveW)

    @staticmethod
    def draw(boss):
        draw_boss_standard(boss)


# =================================================================
# [State 3] 변신 및 우측 상단 이동 (Custom Animation)
# =================================================================
class TransformMoveToCorner:
    @staticmethod
    def enter(boss):
        # 우측 상단 목표
        boss.target_x = 800
        boss.target_y = 650
        boss.speed = 300
        boss.frame = 0.0  # 프레임 초기화

    @staticmethod
    def exit(boss):
        pass

    @staticmethod
    def do(boss):
        # 8프레임 애니메이션
        boss.frame += 1.5 * ACTION_PER_TIME * game_framework.frame_time
        is_anim_finished = False
        if boss.frame >= 7.0:
            boss.frame = 7.0
            is_anim_finished = True

        is_arrived = False
        # 이동 로직
        dx = boss.target_x - boss.x
        dy = boss.target_y - boss.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist < 10:
            boss.x, boss.y = boss.target_x, boss.target_y
            is_arrived = True
        else:
            boss.x += (dx / dist) * boss.speed * game_framework.frame_time
            boss.y += (dy / dist) * boss.speed * game_framework.frame_time
        if is_arrived and is_anim_finished:
            boss.change_state(Phase2_MoveLeftRight)
    @staticmethod
    def draw(boss):
        sx, sy = game_world.world_to_screen(boss.x, boss.y)

        # 현재 프레임 인덱스 (0~7)
        seq_index = int(boss.frame)
        if seq_index >= 8: seq_index = 7
        # 정의해둔 시퀀스에서 Y좌표와 X인덱스를 가져옴
        src_y, frame_idx = TRANSFORM_SEQUENCE[seq_index]
        src_x = frame_idx * FRAME_WIDTH

        # 커스텀 그리기
        boss.image.clip_draw(src_x, src_y, FRAME_WIDTH, FRAME_HEIGHT, sx, sy, boss.width*2.5, boss.height*2.5)


# =================================================================
# [State 4] 2페이즈: 상단 좌우 이동
# =================================================================
class Phase2_MoveLeftRight:
    @staticmethod
    def enter(boss):
        boss.anim_row = ROW_PHASE2
        boss.dir_x = -1
        boss.dir_y = 0
        boss.speed = 200
        boss.attack_cooldown = 2.0

    @staticmethod
    def exit(boss):
        pass

    @staticmethod
    def do(boss):
        boss.frame = (boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        boss.x += boss.dir_x * boss.speed * game_framework.frame_time

        move_left_right_pattern(boss)
        boss.attack_cooldown -= game_framework.frame_time
        if boss.attack_cooldown <= 0:
            # 50% 확률로 공격 패턴 선택
            if random.random() < 0.5:
                boss.change_state(Phase2_AttackSpread)
            else:
                boss.change_state(Phase2_AttackLaser)

    @staticmethod
    def draw(boss):
        draw_boss_standard(boss)


# =================================================================
# [State 5] 2페이즈 공격 1: 5발 갈래 발사
# =================================================================
class Phase2_AttackSpread:
    @staticmethod
    def enter(boss):
        boss.frame = 0.0
        boss.fired = False  # 발사 여부 플래그
        boss.speed = 200

    @staticmethod
    def exit(boss):
        boss.attack_cooldown = random.uniform(1.5, 2.5)  # 공격 후 쿨타임

    @staticmethod
    def do(boss):
        move_left_right_pattern(boss)
        # 5프레임 애니메이션 재생
        # 속도 조절
        boss.frame += 1.5 * ACTION_PER_TIME * game_framework.frame_time

        idx = int(boss.frame)

        # 마지막 프레임(4)에 도달했고 아직 안 쐈다면 발사
        if idx >= 4 and not boss.fired:
            # 5발 발사 로직
            start_angle = -math.pi / 2  # -90도 (아래쪽)
            spread_angles = [-45, -20, 0, 20, 45]

            for deg in spread_angles:
                rad = math.radians(deg) + start_angle
                bullet = BossBullet(boss.x, boss.y, rad)
                game_world.add_object(bullet, 1)
                game_world.add_collision_pair('isaac:boss_bullet',None , bullet)

            boss.fired = True

        # 애니메이션 끝나면 복귀 (5프레임 재생 후)
        if idx >= 5:
            boss.change_state(Phase2_MoveLeftRight)

    @staticmethod
    def draw(boss):
        draw_boss_sequence(boss, ATTACK_SPREAD_SEQ)


# =================================================================
# [State 6] 2페이즈 공격 2: 레이저
# =================================================================
class Phase2_AttackLaser:
    @staticmethod
    def enter(boss):
        boss.frame = 0.0
        boss.laser = None
        boss.speed = 200

    @staticmethod
    def exit(boss):
        boss.attack_cooldown = random.uniform(2.0, 3.0)
        # 상태 나갈 때 레이저 제거 (안전장치)
        if boss.laser:
            game_world.remove_object(boss.laser)
            boss.laser = None

    @staticmethod
    def do(boss):
        move_left_right_pattern(boss)
        # 프레임 애니메이션 재생
        boss.frame += 1.5 * ACTION_PER_TIME * game_framework.frame_time

        idx = int(boss.frame)

        # 6번째(5), 7번째(6) 프레임일 때 레이저 활성화
        if idx == 5 or idx == 6:
            if boss.laser is None:
                boss.laser = BossLaser(boss)
                game_world.add_object(boss.laser, 1)
                game_world.add_collision_pair('isaac:boss_laser',None , boss.laser)
            # 레이저가 있다면 위치는 BossLaser.update에서 자동 갱신됨
        else:
            # 그 외 프레임에선 레이저 제거
            if boss.laser:
                game_world.remove_object(boss.laser)
                boss.laser = None

        # 애니메이션 끝나면 복귀
        if idx >= 7:
            boss.change_state(Phase2_MoveLeftRight)

    @staticmethod
    def draw(boss):
        draw_boss_sequence(boss, ATTACK_LASER_SEQ)

# =================================================================
# Helper Functions
# =================================================================
def handle_wall_bounce_w(boss):
    if common.stage and hasattr(common.stage, 'get_map_bounds'):
        bounds = common.stage.get_map_bounds()
        margin_x = boss.width / 2
        margin_y = boss.height / 2
        map_left = bounds.get('map_left', 0) + margin_x
        map_right = bounds.get('map_right', 1000) - margin_x
        map_bottom = bounds.get('map_bottom', 0) + margin_y
        map_top = bounds.get('map_top', 800) - margin_y

        if boss.x > map_right:
            boss.x = map_right
            boss.dir_x = -1
        elif boss.x < map_left:
            boss.x = map_left
            boss.dir_x = 1

        if boss.y > map_top:
            boss.y = map_top
            boss.dir_y = -1
        elif boss.y < map_bottom:
            boss.y = map_bottom
            boss.dir_y = 1


def draw_boss_standard(boss):
    sx, sy = game_world.world_to_screen(boss.x, boss.y)
    frame_index = int(boss.frame)
    src_x = frame_index * FRAME_WIDTH
    boss.image.clip_draw(src_x, boss.anim_row, FRAME_WIDTH, FRAME_HEIGHT, sx, sy, boss.width * 2.5, boss.height * 2.5)


def draw_boss_sequence(boss, sequence):
    sx, sy = game_world.world_to_screen(boss.x, boss.y)
    idx = int(boss.frame)
    if idx >= len(sequence): idx = len(sequence) - 1

    src_y, frame_idx = sequence[idx]
    src_x = frame_idx * FRAME_WIDTH

    boss.image.clip_draw(src_x, src_y, FRAME_WIDTH, FRAME_HEIGHT, sx, sy, boss.width *2.5, boss.height*2.5)

# =================================================================
# [Boss Class]
# =================================================================
class Boss:
    image = None
    hp_fill_image = None  # 체력바 채움용
    hp_frame_image = None  # [추가] 체력바 틀 이미지
    def __init__(self, x, y):
        if Boss.image is None:
            try:
                Boss.image = load_image('resource/BOSS/Haunt.png')
            except:
                Boss.image = None

        if Boss.hp_fill_image is None:
            try:
                # 레이저 이미지 로드
                Boss.hp_fill_image = load_image('resource/BOSS/laser.png')
            except:
                Boss.hp_fill_image = None

            # 3. 체력바 틀 이미지
        if Boss.hp_frame_image is None:
            try:
                Boss.hp_frame_image = load_image('resource/BOSS/hp_bar.png')
            except:
                Boss.hp_frame_image = None
        self.x, self.y = x, y
        self.width, self.height = FRAME_WIDTH , FRAME_HEIGHT
        self.speed = 150
        self.max_hp = 100
        self.hp = 100

        self.dir_x = 1
        self.dir_y = -1
        self.frame = 0.0
        self.anim_row = ROW_PHASE1

        self.attack_cooldown = 3.0
        self.minions = []

        self.cur_state = MoveW
        self.cur_state.enter(self)

    def change_state(self, new_state):
        self.cur_state.exit(self)
        self.cur_state = new_state
        self.cur_state.enter(self)

    def update(self):
        self.cur_state.do(self)

    def draw(self):
        if self.image:
            self.cur_state.draw(self)
        else:
            draw_rectangle(*self.get_bb())
        self.draw_hp_bar()
    def draw_hp_bar(self):
        frame_x = 500
        frame_y = 50

        if Boss.hp_frame_image is None: return

        frame_w = Boss.hp_frame_image.w * 2
        frame_h = Boss.hp_frame_image.h * 2
        Boss.hp_frame_image.draw(frame_x, frame_y, frame_w, frame_h)
        # --- 1. 붉은색 게이지 (레이저 이미지) 그리기 ---
        if Boss.hp_fill_image:
            padding_x = 34
            padding_y = 18

            inner_max_w = frame_w - (padding_x * 2)
            inner_h = frame_h - (padding_y * 2)

            ratio = max(0, self.hp / self.max_hp)
            current_fill_w = inner_max_w * ratio

            fill_draw_x = (frame_x - frame_w / 2) + padding_x + (current_fill_w / 2)
            fill_draw_y = frame_y

            if current_fill_w > 0:
                Boss.hp_fill_image.clip_draw(
                    40, 40,1,1 ,  # 소스 (이미지 전체)
                    fill_draw_x +15, fill_draw_y -3,  # 위치
                    current_fill_w, inner_h  # 크기 (가로로 늘어남)
                )


    def get_bb(self):
        return self.x - self.width / 2 -30, self.y - self.height / 2 -40, self.x + self.width / 2 + 30, self.y + self.height / 2

    def handle_collision(self, group, other):
        if group == 'boss:tear':
            damage = getattr(other, 'damage', 1)
            self.hp -= damage
            if self.hp <= 0:
                for m in self.minions:
                    m.hp = 0
                game_world.remove_object(self)