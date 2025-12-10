# python
from pico2d import load_image, draw_rectangle
import game_world

class Rock:
    image = None

    def __init__(self, x, y, w=80, h=80):
        if Rock.image is None:
            try:
                Rock.image = load_image('resource/objects/Rock.png')
            except Exception:
                Rock.image = None
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.h = float(h)

    def update(self):
        pass

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Rock.image:
            Rock.image.draw(sx, sy, self.w, self.h)
        else:
            draw_rectangle(sx - self.w/2, sy - self.h/2, sx + self.w/2, sy + self.h/2)
        #
        # l, b, r, t = self.get_bb()
        # ls, bs = game_world.world_to_screen(l, b)
        # rs, ts = game_world.world_to_screen(r, t)
        # draw_rectangle(ls, bs, rs, ts)

    def get_bb(self):
        return (self.x - self.w/2, self.y - self.h/2, self.x + self.w/2, self.y + self.h/2)

    def handle_collision(self, group, other):
        return
