from pico2d import *
import game_world
import common
from hp_potion import HPPotion


class Machine:
    image = None

    def __init__(self, x, y):
        if Machine.image is None:
            try:
                Machine.image = load_image('resource/objects/machine.png')
            except Exception:
                Machine.image = None

        self.x, self.y = x, y
        self.width = 60
        self.height = 60

        # 구매 쿨타임 (연속 구매 방지)
        self.buy_cooldown = 1.0
        self.price = 3  # 물약 가격 (코인 3개)

    def update(self):
        if self.buy_cooldown > 0:
            self.buy_cooldown -= 0.01  # 간단한 타이머 감소

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Machine.image:
            Machine.image.draw(sx, sy, self.width, self.height)
        else:
            # 이미지가 없으면 파란색 네모
            draw_rectangle(sx - 30, sy - 30, sx + 30, sy + 30)

        # 디버깅용 박스
        l, b, r, t = self.get_bb()
        sl, sb = game_world.world_to_screen(l, b)
        sr, st = game_world.world_to_screen(r, t)
        draw_rectangle(sl, sb, sr, st)

    def get_bb(self):
        return self.x - 30, self.y - 30, self.x + 30, self.y + 30

    def handle_collision(self, group, other):
        if group == 'isaac:machine':
            # 쿨타임 중이면 무시
            if self.buy_cooldown > 0:
                return

            # 코인이 충분한지 확인
            if common.isaac and common.isaac.coin_count >= self.price:
                common.isaac.coin_count -= self.price
                self.spawn_potion()
                self.buy_cooldown = 1.0  # 1초 쿨타임
                print("Potion Bought!")
            else:
                print("Not enough coins!")

    def spawn_potion(self):
        # 머신 바로 아래쪽에 물약 생성
        potion = HPPotion(self.x, self.y - 50)
        game_world.add_object(potion, 1)

        # 충돌 등록 (isaac과 물약)
        if common.isaac:
            game_world.add_collision_pair('isaac:hp_potion', common.isaac, potion)