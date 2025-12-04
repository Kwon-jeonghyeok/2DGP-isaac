# python
from pico2d import load_image, draw_rectangle
import game_world

class Poo:
    image = None
    FRAMES = 5

    def __init__(self, x, y, w=70, h=70):
        if Poo.image is None:
            try:
                Poo.image = load_image('resource/objects/Poop.png')
            except Exception:
                Poo.image = None
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.h = float(h)

        self.frame = 0           # 현재 표시할 프레임 (0..4)
        self.hit_count = 0       # 맞은 횟수
        self.collidable = True   # 충돌 판정 활성화 여부
        self.destroyed = False   # 완전 제거 플래그 (필요시 사용)

    def update(self):
        # 정적 오브젝트
        pass

    def draw(self):
        if self.destroyed:
            return
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if Poo.image:
            fw = int(Poo.image.w // Poo.FRAMES)
            fh = int(Poo.image.h)
            Poo.image.clip_draw(self.frame * fw, 0, fw, fh, sx, sy, self.w, self.h)

        else:
            draw_rectangle(sx - self.w / 2, sy - self.h / 2,
                           sx + self.w / 2, sy + self.h / 2)
        l, b, r, t = self.get_bb()
        ls, bs = game_world.world_to_screen(l, b)
        rs, ts = game_world.world_to_screen(r, t)
        draw_rectangle(ls, bs, rs, ts)

    def get_bb(self):
        # 충돌 판정이 비활성화된 경우 0 영역 반환
        if not self.collidable or self.destroyed:
            return 0, 0, 0, 0
        return (self.x - self.w / 2, self.y - self.h / 2,
                self.x + self.w / 2, self.y + self.h / 2)

    def destroy(self):
        try:
            game_world.remove_object(self)
        except Exception:
            pass
        self.destroyed = True

    def handle_collision(self, group, other):
        if ':tear' in group:
            if not self.collidable or self.destroyed:
                return
            # 히트 처리: 프레임 증가
            self.hit_count += 1
            # 프레임은 0..FRAMES-1
            self.frame = min(self.hit_count, Poo.FRAMES - 1)
            # 마지막 프레임(인덱스 FRAMES-1) 이후에는 충돌 판정만 제거
            if self.hit_count >= Poo.FRAMES - 1:
                self.collidable = False
                try:
                    game_world.remove_collision_object(self)
                except Exception:
                    pass
        return
