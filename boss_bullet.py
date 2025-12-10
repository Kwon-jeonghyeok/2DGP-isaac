from pico2d import *
import game_world
import game_framework
import math


class BossBullet:
    image = None

    def __init__(self, x, y, angle):
        if BossBullet.image is None:
            try:
                # 보스 총알 이미지는 기존 Tears를 붉게 쓰거나 Blood Tears 사용
                BossBullet.image = load_image('resource/objects/tears.png')
            except:
                BossBullet.image = None

        self.x, self.y = x, y
        self.speed = 350.0
        self.angle = angle  # 발사 각도 (라디안)

        # 붉은색 틴트 효과를 위해 (선택사항)
        # self.color = (255, 0, 0)

    def update(self):
        # 각도에 따라 이동
        self.x += math.cos(self.angle) * self.speed * game_framework.frame_time
        self.y += math.sin(self.angle) * self.speed * game_framework.frame_time

        # 화면 밖으로 나가면 제거
        if self.x < 0 or self.x > 1000 or self.y < 0 or self.y > 800:
            game_world.remove_object(self)

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if BossBullet.image:

            BossBullet.image.clip_draw(600, 470, 30, 30, sx, sy, 40, 40)
        else:
            draw_rectangle(sx - 10, sy - 10, sx + 10, sy + 10)

        # 디버그
        #draw_rectangle(*self.get_bb_screen())

    def get_bb(self):
        return self.x - 10, self.y - 10, self.x + 10, self.y + 10

    def get_bb_screen(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        return sx - 10, sy - 10, sx + 10, sy + 10

    def handle_collision(self, group, other):
        if group == 'isaac:boss_bullet':
            game_world.remove_object(self)
            # 충돌 처리 시스템에서도 안전하게 제거
            try:
                game_world.remove_collision_object(self)
            except:
                pass