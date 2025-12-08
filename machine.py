from pico2d import *
import game_world
import game_framework
import common
import random
from hp_potion import HPPotion

# 머신 애니메이션 속도 설정
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 3.0


class Machine:
    image = None

    def __init__(self, x, y):
        if Machine.image is None:
            try:
                Machine.image = load_image('resource/objects/machine.png')
            except Exception:
                Machine.image = None

        self.x, self.y = x, y

        self.frame_width = 51
        self.frame_height = 60
        if Machine.image:
            self.frame_height = Machine.image.h

        self.width = 100
        self.height = 100

        self.price = 3
        self.buy_cooldown = 0.0

        self.state = 'IDLE'
        self.frame = 0.0
        self.potion_spawned = False

    def update(self):
        if self.buy_cooldown > 0:
            self.buy_cooldown -= game_framework.frame_time

        if self.state == 'ACTIVE':
            self.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
            curr_idx = int(self.frame)

            if curr_idx == 2 and not self.potion_spawned:
                self.spawn_potion()
                self.potion_spawned = True

            if curr_idx >= 3:
                self.state = 'IDLE'
                self.frame = 0.0
                self.potion_spawned = False

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)

        if Machine.image:
            frame_idx = 0
            if self.state == 'ACTIVE':
                frame_idx = int(self.frame) % 3

            Machine.image.clip_draw(
                frame_idx * self.frame_width, 0,
                self.frame_width, self.frame_height,
                sx, sy,
                self.width, self.height
            )
        else:
            draw_rectangle(sx - 25, sy - 25, sx + 25, sy + 25)

    def get_bb(self):
        return self.x - 25, self.y - 25, self.x + 25, self.y + 25

    def handle_collision(self, group, other):
        if group == 'isaac:machine':
            if self.state == 'ACTIVE' or self.buy_cooldown > 0:
                return

            if common.isaac and common.isaac.coin_count >= self.price:
                common.isaac.coin_count -= self.price

                self.state = 'ACTIVE'
                self.frame = 0.0
                self.potion_spawned = False
                self.buy_cooldown = 1.0
            else:
                pass

    def spawn_potion(self):
        rx = random.randint(-40, 40)
        ry = random.randint(-60, -30)  # 머신보다 약간 아래쪽에 떨어지도록

        drop_x = self.x + rx
        drop_y = self.y + ry

        potion = HPPotion(drop_x, drop_y)
        game_world.add_object(potion, 1)

        if common.isaac:
            game_world.add_collision_pair('isaac:hp_potion', common.isaac, potion)