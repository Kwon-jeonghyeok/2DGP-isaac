from pico2d import *
import game_world


class Coin:
    image = None

    def __init__(self, x, y):
        if Coin.image is None:
            try:
                Coin.image = load_image('resource/objects/coin.png')
            except Exception:
                print("Coin image not found")
                Coin.image = None

        self.x, self.y = x, y
        self.width = 30
        self.height = 30

    def update(self):
        # 필요하다면 애니메이션 추가 가능
        pass

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Coin.image:
            Coin.image.draw(sx, sy, self.width, self.height)
        else:
            draw_rectangle(sx - 15, sy - 15, sx + 15, sy + 15)

        # 디버깅용 박스 (필요시 주석 해제)
        draw_rectangle(*self.get_bb_screen())

    def get_bb(self):
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def get_bb_screen(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        return sx - 15, sy - 15, sx + 15, sy + 15

    def handle_collision(self, group, other):
        if group == 'isaac:coin':
            game_world.remove_object(self)