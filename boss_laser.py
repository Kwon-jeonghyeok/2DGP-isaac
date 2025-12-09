from pico2d import *
import game_world
import game_framework


class BossLaser:
    def __init__(self, owner):
        self.owner = owner  # 보스 객체 참조
        self.x = owner.x
        self.y = owner.y - 400  # 보스 아래쪽으로 길게

        self.width = 60
        self.height = 800  # 맵 전체 높이 커버

        # 레이저 지속시간이나 프레임 관리는 Boss 상태에서 제어하므로
        # 여기서는 단순히 따라다니고 충돌박스만 제공

    def update(self):
        # 보스가 죽거나 없으면 같이 사라짐
        if self.owner is None or self.owner.hp <= 0:
            game_world.remove_object(self)
            return

        # [핵심] 보스의 X 위치를 실시간으로 따라다님
        self.x = self.owner.x
        # Y 위치는 보스 중심보다 아래쪽으로 설정 (바닥까지 닿게)
        # 맵 높이가 800이고 보스가 700쯤 있으므로, 중심은 대략 350쯤 잡으면 됨
        self.y = self.owner.y - (self.height / 2) + 50

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        # 레이저 이미지 (없으면 붉은색 사각형)
        # 반투명 붉은색으로 그리기 (블렌딩 등은 복잡하므로 단순 사각형)
        draw_rectangle(sx - self.width / 2, sy - self.height / 2,
                       sx + self.width / 2, sy + self.height / 2)

    def get_bb(self):
        return self.x - self.width / 2, self.y - self.height / 2, self.x + self.width / 2, self.y + self.height / 2

    def handle_collision(self, group, other):
        pass  # 레이저는 관통하므로 충돌해도 사라지지 않음