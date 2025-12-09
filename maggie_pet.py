from pico2d import *
import game_world
import game_framework
import common
from tear import Tear


class MaggiePet:
    image = None
    # 메기펫 스프라이트 한 칸의 크기 (아이작과 동일하게 64x64로 가정)
    # 만약 이미지가 잘려 보이거나 밀리면 이 값을 실제 이미지에 맞춰 수정해주세요.
    FRAME_WIDTH, FRAME_HEIGHT = 32, 32

    def __init__(self, x, y):
        if MaggiePet.image is None:
            try:
                # [수정] 실제 이미지 파일 로드
                MaggiePet.image = load_image('resource/maggie.png')
            except:
                print("ERROR: Could not load 'resource/maggie.png'")
                MaggiePet.image = None

        self.x, self.y = x, y
        self.state = 'WAITING'
        self.price = 5
        # 충돌 박스 크기 
        self.width, self.height = 40, 40

        # 아이작 기준 상대 위치 (왼쪽 상단)
        self.offset_x = -40
        self.offset_y = 40


        self.face_dir = 0  # 아이작의 방향
        self.y_dir = 0  # 아이작의 수직 방향
        self.is_attacking = False
        self.attack_duration = 0.2  # 공격 프레임을 보여줄 시간(초)
        self.attack_timer = 0.0

    def update(self):
        # 구매된 상태라면 아이작을 따라다님
        if self.state == 'FOLLOWING':
            if common.isaac:
                self.x = common.isaac.x + self.offset_x
                self.y = common.isaac.y + self.offset_y
                #아이작이 보는 방향을 동기화
                self.face_dir = common.isaac.face_dir
                self.y_dir = common.isaac.y_dir

        if self.is_attacking:
            self.attack_timer += game_framework.frame_time
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.attack_timer = 0.0

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)

        if MaggiePet.image is None:
            draw_rectangle(sx - 20, sy - 20, sx + 20, sy + 20)
            return

        # 방향과 상태에 따른 프레임 인덱스 및 반전 여부 결정
        frame_index = 0
        flip_h = False  # 좌우 반전 여부


        if  self.y_dir == -1:  # 아래 (기본)
            frame_index = 1 if self.is_attacking else 0
        elif self.y_dir == 1:  # 위
            frame_index = 5 if self.is_attacking else 4
        elif self.face_dir == -1:  # 왼쪽 (반전 필요)
            frame_index = 3 if self.is_attacking else 2
            flip_h = True
        elif self.face_dir == 1:  # 오른쪽
            frame_index = 3 if self.is_attacking else 2

        # 스프라이트 시트 내에서의 X 좌표 계산
        frame_x = frame_index * MaggiePet.FRAME_WIDTH

        # 화면에 그릴 크기
        draw_w, draw_h = 48,48

        if flip_h:
            # 좌우 반전 그리기
            MaggiePet.image.clip_composite_draw(
                frame_x, 0,MaggiePet.FRAME_WIDTH,MaggiePet.FRAME_HEIGHT,0,'h',sx, sy,draw_w, draw_h)
        else:
            if self.y_dir == 1:
                MaggiePet.image.clip_draw(frame_x, 0,MaggiePet.FRAME_WIDTH,MaggiePet.FRAME_HEIGHT,sx, sy,draw_w, draw_h)
            else:
                MaggiePet.image.clip_draw(frame_x, 0,MaggiePet.FRAME_WIDTH,MaggiePet.FRAME_HEIGHT,sx, sy,draw_w, draw_h)
    def get_bb(self):
        # 충돌 박스 크기 조정 (width/height 속성 사용)
        half_w, half_h = self.width / 2, self.height / 2
        return self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

    def handle_collision(self, group, other):
        if self.state == 'WAITING':
            if group == 'isaac:maggie_pet':
                if common.isaac and common.isaac.coin_count >= self.price:
                    # 구매 성공
                    common.isaac.coin_count -= self.price
                    self.state = 'FOLLOWING'

                    # 아이작에게 펫 등록
                    common.isaac.pet = self

                    game_world.remove_collision_object(self)
                    game_world.remove_object(self)
                    game_world.add_object(self, 2)

    def fire_tear(self, face_dir, damage):
        self.is_attacking = True
        self.attack_timer = 0.0

        tear = Tear(self.x, self.y, face_dir, damage=damage)
        game_world.add_object(tear, 1)

        game_world.add_collision_pair('host:tear', None, tear)
        game_world.add_collision_pair('sucker:tear', None, tear)
        game_world.add_collision_pair('poo:tear', None, tear)
        game_world.add_collision_pair('rock:tear', None, tear)
        game_world.add_collision_pair('charger:tear', None, tear)
        game_world.add_collision_pair('boss:tear', None, tear)
        game_world.add_collision_pair('lilhaunt:tear', None, tear)