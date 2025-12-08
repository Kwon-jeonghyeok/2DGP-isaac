from pico2d import *
import game_world
import common


class HPPotion:
    image = None

    def __init__(self, x, y):
        if HPPotion.image is None:
            try:
                HPPotion.image = load_image('resource/objects/Heart.png')
            except Exception:
                HPPotion.image = None

        self.x, self.y = x, y
        self.width = 30
        self.height = 30

    def update(self):
        pass

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if HPPotion.image:
            HPPotion.image.draw(sx, sy, self.width, self.height)
        else:
            # 이미지가 없으면 빨간색 네모로 표시
            draw_rectangle(sx - 15, sy - 15, sx + 15, sy + 15)

    def get_bb(self):
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def handle_collision(self, group, other):
        if group == 'isaac:hp_potion':
            # 아이작 쪽에서 회복 처리를 하고 여기서는 객체만 삭제
            game_world.remove_object(self)