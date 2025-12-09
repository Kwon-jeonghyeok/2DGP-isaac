from pico2d import *
import game_world
import game_framework
import common
PIXEL_PER_METER = (1.0 / 0.015)

TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 20

class Tear:
    image = None

    def __init__(self, x=400, y=300, face_dir=1, max_range=400, damage = 1):
        if Tear.image == None:
            Tear.image = load_image('resource/objects/tears.png')
        self.x, self.y, self.dir = x, y, face_dir
        # 시작 위치(사거리 계산에 사용)
        self.start_x, self.start_y = x, y
        # 최대 사거리(픽셀 단위)
        self.max_range = max_range
        self.traveled = 0.0
        self.damage = damage
        if self.damage >= 2:
            self.frame_y = 470
            self.frame_x = 600
        else:
            self.frame_y = 215
            self.frame_x = 280

        # 이동/폭발 상태 관리
        self.moving = True
        self.frame = 0.0
        # 폭발 애니메이션 프레임(실수로 시간기반 증가)
        self.explosion_frame = 0.0
        # 폭발 프레임 수: 총 8프레임 (첫 4는 같은 행, 다음 4는 같은 x에서 y만 아래)
        self.EXPLOSION_FRAMES = 8

        self.consumed = False

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if self.moving:
            self.image.clip_draw(self.frame_x, self.frame_y, 30, 30, sx, sy, 40, 40)
        else:
            # 폭발 애니메이션: 총 8프레임
            frame_index = int(self.explosion_frame)
            frame_w, frame_h = 30, 30
            # 한 행에 4프레임
            sub_index = frame_index % 4
            src_x = self.frame_x + sub_index * (frame_w * 2)
            # 첫 4프레임은 src_y_row0, 다음 4프레임은 src_y_row1(아래쪽)
            src_y_row0 = self.frame_y
            src_y_row1 = src_y_row0 - (frame_h*2)  # 아래로 이동한 행
            src_y = src_y_row0 if frame_index < 4 else src_y_row1
            self.image.clip_draw(src_x, src_y, frame_w, frame_h, sx, sy, 40, 40)
            #draw_rectangle(*self.get_bb())

        la, ba, ra, ta = self.get_bb()
        ls, bs = game_world.world_to_screen(la, ba)
        rs, ts = game_world.world_to_screen(ra, ta)
        draw_rectangle(ls, bs, rs, ts)
    def update(self):

        # 이동 중일 때
        if self.moving:

            #self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 4

            # 속도(픽셀/업데이트)
            step = PIXEL_PER_METER * ACTION_PER_TIME * game_framework.frame_time * 5

            if self.dir == 1:
                self.x += step
            elif self.dir == -1:
                self.x -= step
            elif self.dir == 2:
                self.y += step
            elif self.dir == 0:
                self.y -= step

            # 사거리 누적
            self.traveled += step

            # 사거리 도달
            if self.traveled >= self.max_range:
                self.moving = False
                self.explosion_frame = 0.0
                return
            margin = 0

            # 2. 스테이지 3일 때만 다른 마진 적용
            # common.stage가 존재하고, 그 클래스 이름이 'Stage_3'인지 확인
            if common.stage and common.stage.__class__.__name__ == 'Stage_3':
                margin = 75  # 예: Stage 3는 벽에 더 가까이 붙어야 터지게 설정 (원하는 값으로 수정!)

            # 3. 현재 스테이지의 경계 가져오기 (common.stage 사용)
            map_left, map_right, map_bottom, map_top = 0, 1000, 0, 800  # 안전용 기본값

            if common.stage and hasattr(common.stage, 'get_map_bounds'):
                bounds = common.stage.get_map_bounds()
                map_left = bounds.get('map_left', map_left)
                map_right = bounds.get('map_right', map_right)
                map_bottom = bounds.get('map_bottom', map_bottom)
                map_top = bounds.get('map_top', map_top)

            # 4. 결정된 마진(margin)과 경계(bounds)로 충돌 검사
            if self.x < map_left + margin or self.x > map_right - margin  or \
                    self.y < map_bottom or self.y > map_top + margin :
                self.moving = False
                self.explosion_frame = 0.0
                return
        else:
            # 폭발 애니메이션 속도(프레임/초 기반)
            self.explosion_frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time

            # 애니메이션이 끝나면 객체 제거
            if int(self.explosion_frame) >= self.EXPLOSION_FRAMES:
                game_world.remove_object(self)

    def get_bb(self):
        if self.moving:
            return self.x - 22, self.y - 16, self.x + 4, self.y + 6
        else:
            return self.x - 10, self.y - 6, self.x , self.y

    def handle_collision(self, group, other):

        if group in ('host:tear', 'sucker:tear', 'poo:tear', 'rock:tear','charger:tear'):
            if self.consumed:
                return
            self.consumed = True
            self.moving = False
            self.explosion_frame = 0.0
            try:
                game_world.remove_collision_object(self)
            except Exception:
                pass
            return
        pass