# python
from pico2d import load_image, draw_rectangle
import game_world

class Poo:
    image = None

    def __init__(self, x, y, w=40, h=40):
        if Poo.image is None:
            try:
                Poo.image = load_image('resource/objects/poo.png')
            except Exception:
                Poo.image = None
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.h = float(h)
        self.destroyed = False

    def update(self):
        # 정적 오브젝트
        pass

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Poo.image:
            Poo.image.draw(sx, sy, self.w, self.h)
        else:
            draw_rectangle(sx - self.w/2, sy - self.h/2, sx + self.w/2, sy + self.h/2)

        l, b, r, t = self.get_bb()
        ls, bs = game_world.world_to_screen(l, b)
        rs, ts = game_world.world_to_screen(r, t)
        draw_rectangle(ls, bs, rs, ts)

    def get_bb(self):
        return (self.x - self.w/2, self.y - self.h/2, self.x + self.w/2, self.y + self.h/2)

    def handle_collision(self, group, other):
        # 오직 눈물 그룹과 충돌할 때만 제거
        if ':tear' in group:
            if self.destroyed:
                return
            self.destroyed = True
            try:
                game_world.remove_collision_object(self)
            except Exception:
                pass
            try:
                game_world.remove_object(self)
            except Exception:
                pass
        return
