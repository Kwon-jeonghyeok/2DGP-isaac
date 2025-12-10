from pico2d import *
import game_world
import common


class DamageItem:
    image = None

    def __init__(self, x, y):
        if DamageItem.image is None:
            try:
                DamageItem.image = load_image('resource/objects/damage_item.png')
            except Exception:
                DamageItem.image = None

        self.x, self.y = x, y
        self.width = 80
        self.height = 120
        self.price = 3

    def update(self):
        pass

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if DamageItem.image:
            DamageItem.image.draw(sx, sy, self.width, self.height)
        else:
            # 이미지가 없으면 붉은색 네모 (공격력 느낌)
            draw_rectangle(sx - 20, sy - 20, sx + 20, sy + 20)

        # 가격 표시 (선택 사항)
        # 폰트가 있다면 여기에 가격을 그려줄 수도 있습니다.

    def get_bb(self):
        return self.x - 20, self.y - 20, self.x + 20, self.y + 20

    def handle_collision(self, group, other):
        if group == 'isaac:damage_item':
            if other.coin_count >= self.price:
                game_world.remove_object(self)