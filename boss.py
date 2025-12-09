from pico2d import *
import game_framework
import game_world
import common

# =================================================================
# 보스 이미지 및 애니메이션 상수
# =================================================================
FRAME_WIDTH = 100  # 프레임 너비 (실제 이미지에 맞게 수정!)
FRAME_HEIGHT = 100  # 프레임 높이
SHEET_HEIGHT = 500  # 시트 전체 높이
TOP_ROW_Y = SHEET_HEIGHT - FRAME_HEIGHT  # 맨 윗줄 Y좌표

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 3  # 3프레임 애니메이션


# =================================================================
# [State 1] W 이동 상태 (기본 패턴)
# =================================================================
class MoveW:
    @staticmethod
    def enter(boss):
        # 초기 방향 설정
        boss.dir_y = -1
        if boss.dir_x == 0:
            boss.dir_x = 1
        boss.timer = 0

    @staticmethod
    def exit(boss):
        pass

    @staticmethod
    def do(boss):
        # 1. 애니메이션
        boss.frame = (boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION

        # 2. 이동 (대각선)
        boss.x += boss.dir_x * boss.speed * game_framework.frame_time
        boss.y += boss.dir_y * boss.speed * game_framework.frame_time

        # 3. 벽 튕기기 (W 패턴)
        if common.stage and hasattr(common.stage, 'get_map_bounds'):
            bounds = common.stage.get_map_bounds()
            margin_x = boss.width / 2
            margin_y = boss.height / 2

            map_left = bounds.get('map_left', 0) + margin_x
            map_right = bounds.get('map_right', 1000) - margin_x
            map_bottom = bounds.get('map_bottom', 0) + margin_y
            map_top = bounds.get('map_top', 800) - margin_y

            # 좌우 벽 -> 방향 반전
            if boss.x > map_right:
                boss.x = map_right
                boss.dir_x = -1
            elif boss.x < map_left:
                boss.x = map_left
                boss.dir_x = 1

            # 상하 벽 -> 방향 반전
            if boss.y > map_top:
                boss.y = map_top
                boss.dir_y = -1
            elif boss.y < map_bottom:
                boss.y = map_bottom
                boss.dir_y = 1

    @staticmethod
    def draw(boss):
        sx, sy = game_world.world_to_screen(boss.x, boss.y)
        frame_index = int(boss.frame)
        src_x = frame_index * FRAME_WIDTH

        boss.image.clip_draw(src_x, TOP_ROW_Y, FRAME_WIDTH, FRAME_HEIGHT, sx, sy, boss.width, boss.height)


# =================================================================
# [Boss Class] 보스 본체
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
        self.width, self.height = FRAME_WIDTH * 2.5, FRAME_HEIGHT * 2.5
        self.speed = 150
        self.hp = 100

        self.dir_x = 1
        self.dir_y = -1
        self.frame = 0.0
        self.timer = 0.0

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
        return self.x - self.width / 2, self.y - self.height / 2, self.x + self.width / 2, self.y + self.height / 2

    def handle_collision(self, group, other):
        pass