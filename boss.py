from pico2d import *
import game_framework
import game_world
import common
import random
import math

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

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 3


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
        print("BOSS PHASE 2: Transform Sequence Start")
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
        if boss.frame >= 7.0:
            boss.frame = 7.0
        # 이동 로직
        dx = boss.target_x - boss.x
        dy = boss.target_y - boss.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist < 10:
            boss.x, boss.y = boss.target_x, boss.target_y
            boss.change_state(Phase2_MoveLeftRight)
        else:
            boss.x += (dx / dist) * boss.speed * game_framework.frame_time
            boss.y += (dy / dist) * boss.speed * game_framework.frame_time

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
        boss.speed = 400

    @staticmethod
    def exit(boss):
        pass

    @staticmethod
    def do(boss):
        boss.frame = (boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        boss.x += boss.dir_x * boss.speed * game_framework.frame_time

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

    @staticmethod
    def draw(boss):
        draw_boss_standard(boss)


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


# =================================================================
# [Boss Class]
# =================================================================
class Boss:
    image = None

    def __init__(self, x, y):
        if Boss.image is None:
            try:
                Boss.image = load_image('resource/BOSS/Haunt.png')
            except:
                Boss.image = None

        self.x, self.y = x, y
        self.width, self.height = FRAME_WIDTH , FRAME_HEIGHT
        self.speed = 150
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