from pico2d import *
import game_world
import game_framework

class BossLaser:
    image = None

    def __init__(self, owner):
        self.owner = owner  # 보스 객체 참조

        if BossLaser.image is None:
            try:

                BossLaser.image = load_image('resource/BOSS/laser.png')
            except:
                BossLaser.image = None

        self.x = owner.x -10
        # 보스 중심에서 약간 아래쪽부터 바닥까지 커버
        self.y = owner.y - 400
        self.laser = load_wav('resource/sound/boss_laser.mp3')
        self.laser.set_volume(15)

        self.laser.play(1)

        self.width = 120  # 레이저 두께
        self.height = 800  # 맵 전체 높이 커버

        # 실제 충돌 박스 너비
        self.bb_width = 80

    def update(self):
        # 보스가 죽거나 없으면 같이 사라짐
        if self.owner is None or self.owner.hp <= 0:
            game_world.remove_object(self)
            return

        # 보스의 X 위치를 실시간으로 따라다님
        self.x = self.owner.x -10
        # Y 위치와 높이 재설정 (보스 위치에 따라 유동적으로)
        # 보스 발밑부터 맵 최하단(0)까지
        bottom_y = 0
        top_y = self.owner.y - 50  # 보스 몸체 약간 아래
        self.y = (top_y + bottom_y) / 2
        self.height = top_y - bottom_y

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)

        if BossLaser.image:
            BossLaser.image.draw(sx, sy, self.width, self.height)
        else:
            draw_rectangle(*self.get_bb_screen())

    def get_bb(self):
        # 충돌 박스는 이미지보다 약간 좁게 설정
        return self.x - self.bb_width / 2, self.y - self.height / 2, self.x + self.bb_width / 2, self.y + self.height / 2

    def get_bb_screen(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        return sx - self.bb_width / 2, sy - self.height / 2, sx + self.bb_width / 2, sy + self.height / 2

    def handle_collision(self, group, other):
        pass  # 레이저는 관통하므로 충돌해도 사라지지 않음