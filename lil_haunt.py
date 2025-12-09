from pico2d import *
import game_world
import game_framework
import common
import math
import random
from coin import Coin

# 상태 상수
STATE_ORBIT = 0  # 보스 주위 회전
STATE_CHASE = 1  # 아이작 추적
STATE_RETURN = 2  # 보스에게 복귀


class LilHaunt:
    image = None

    def __init__(self, boss, index, total):
        if LilHaunt.image is None:
            try:
                LilHaunt.image = load_image('resource/monster/Lil_Haunt.png')
            except:
                LilHaunt.image = None

        self.boss = boss
        self.state = STATE_ORBIT

        # 이미지 설정 (2개 표정 중 하나 선택)
        self.frame_index = index % 2
        self.width, self.height = 30, 30

        # 회전 관련 변수
        self.orbit_radius = 60.0  # 보스와의 거리
        self.angle = (2 * math.pi / total) * index  # 3마리가 균등하게 배치되도록 각도 설정
        self.orbit_speed = 3.0  # 회전 속도

        # 이동 관련 변수
        self.x, self.y = boss.x, boss.y  # 초기 위치
        self.speed = 200.0  # 추적 속도

        self.hp = 3

    def update(self):
        dt = game_framework.frame_time

        # 보스가 죽거나 없으면 같이 소멸 (또는 독자 행동)
        if self.boss is None or self.boss.hp <= 0:
            self.hp = 0  # 즉시 사망 처리

        if self.hp <= 0:
            self.destroy()
            return

        if self.state == STATE_ORBIT:
            # 보스 주위를 돎
            self.angle += self.orbit_speed * dt
            self.x = self.boss.x + math.cos(self.angle) * self.orbit_radius
            self.y = self.boss.y + math.sin(self.angle) * self.orbit_radius

        elif self.state == STATE_CHASE:
            # 아이작을 향해 이동
            if common.isaac:
                dx, dy = common.isaac.x - self.x, common.isaac.y - self.y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist > 0:
                    self.x += (dx / dist) * self.speed * dt
                    self.y += (dy / dist) * self.speed * dt

            # 추적 중에도 보스와의 각도는 계속 갱신해둠 (복귀 시 자연스럽게)
            self.angle += self.orbit_speed * dt

        elif self.state == STATE_RETURN:
            # 보스 곁(원래 궤도)으로 복귀
            target_x = self.boss.x + math.cos(self.angle) * self.orbit_radius
            target_y = self.boss.y + math.sin(self.angle) * self.orbit_radius

            dx, dy = target_x - self.x, target_y - self.y
            dist = math.sqrt(dx ** 2 + dy ** 2)

            # 목표 지점에 거의 도달했으면 다시 ORBIT 상태로 전환
            if dist < 10:
                self.state = STATE_ORBIT
            else:
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt
                # 복귀 중에도 각도 갱신
                self.angle += self.orbit_speed * dt

    def draw(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        if LilHaunt.image:
            fw = LilHaunt.image.w // 2
            fh = LilHaunt.image.h

            LilHaunt.image.clip_draw(self.frame_index * fw, 0, fw, fh, sx, sy, 70, 70)
        else:
            draw_rectangle(sx - 15, sy - 15, sx + 15, sy + 15)

        draw_rectangle(*self.get_bb_screen())

    def get_bb(self):
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def get_bb_screen(self):
        sx, sy = game_world.world_to_screen(self.x, self.y)
        return sx - 15, sy - 15, sx + 15, sy + 15

    def handle_collision(self, group, other):
        if group == 'lilhaunt:tear':
            damage = getattr(other, 'damage', 1)
            self.hp -= damage
            if self.hp <= 0:
                self.destroy()

    def destroy(self):
        try:
            # 게임 월드에서 제거 시도
            game_world.remove_object(self)
        except Exception:
            return

        # 보스의 하수인 리스트에서 제거
        if self.boss and hasattr(self.boss, 'minions'):
            try:
                if self in self.boss.minions:
                    self.boss.minions.remove(self)
            except ValueError:
                pass

    # 외부(보스)에서 상태를 변경하는 메서드
    def start_chase(self):
        self.state = STATE_CHASE
        print("LilHaunt: Start Chase!")

    def return_to_boss(self):
        self.state = STATE_RETURN