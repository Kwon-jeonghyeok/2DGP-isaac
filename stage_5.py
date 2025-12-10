from pico2d import *
import game_world
import common
from boss import Boss
from lil_haunt import LilHaunt
import play_mode


class Stage_5:
    def __init__(self):


        self.boss = None
        try:
            # 보스룸 배경 이미지 로드
            self.image = load_image('resource/rooms/Boss_Room.png')
        except Exception:
            print("ERROR: Boss_Room.png not found")
            self.image = None





        self.is_cleared = False  # 보스를 잡기 전까진 닫혀 있어야 함 (추후 구현)
        self.minions = []  # 스테이지 레벨에서 관리할 리스트

    def get_map_bounds(self):
        # Stage 4와 동일한 맵 크기
        return {
            'map_left': 100,
            'map_right': 875,
            'map_bottom': 175,
            'map_top': 700,
            'notches': []
        }

    def update(self):
        pass

    def draw(self):
        # 배경 그리기 (Stage 4와 같은 좌표계 사용)
        if self.image:
            self.image.draw(250, 600, 500, 400)
            self.image.composite_draw(0, 'h', 750, 600, 500, 400)
            self.image.composite_draw(0, 'v', 250, 200, 500, 400)
            self.image.composite_draw(0, 'hv', 750, 200, 500, 400)

    def ensure_obstacles(self):

        # 보스 생성
        if self.boss is None:

            self.boss = Boss(487, 600)

            # 잡몹 3마리 생성
            self.minions = []
            for i in range(3):
                # boss, index, total_count 전달
                minion = LilHaunt(self.boss, i, 3)
                self.minions.append(minion)

            # 보스에게 잡몹 리스트 전달
            self.boss.minions = self.minions

        # 월드 등록
        if self.boss not in sum(game_world.world, []):
            game_world.add_object(self.boss, 1)
            game_world.add_collision_pair('boss:tear', self.boss, None)
            game_world.add_collision_pair('isaac:boss', None, self.boss)

        # 잡몹 월드 등록 및 충돌 설정
        for m in self.minions:
            if m.hp > 0 and m not in sum(game_world.world, []):
                game_world.add_object(m, 1)
                # 충돌 그룹 등록 (play_mode에서 하는게 정석이지만 안전장치)
                game_world.add_collision_pair('isaac:lilhaunt', common.isaac, m)
                game_world.add_collision_pair('lilhaunt:tear', m, None)

    def clear_obstacles(self):
        if self.boss:
            game_world.remove_object(self.boss)

        for m in self.minions:
            try:
                game_world.remove_object(m)
            except:
                pass