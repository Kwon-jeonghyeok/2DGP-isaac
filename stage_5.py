from pico2d import load_image
import game_world
import common
from boss import Boss

class Stage_5:
    def __init__(self):
        self.boss = None
        try:
            # 보스룸 배경 이미지 로드
            self.image = load_image('resource/rooms/Boss_Room.png')
        except Exception:
            print("ERROR: Boss_Room.png not found")
            self.image = None

        try:
            self.image2 = load_image('resource/objects/Door_1.png')
        except Exception:
            self.image2 = None

        self.is_cleared = False  # 보스를 잡기 전까진 닫혀 있어야 함 (추후 구현)

    def get_map_bounds(self):
        # Stage 4와 동일한 맵 크기
        return {
            'map_left': 100,
            'map_right': 875,
            'map_bottom': 175,
            'map_top': 700,
            'notches': [
                # 아래쪽 문 (Stage 4로 돌아가는 문)
                {'x': 490, 'y': 175, 'w': 50, 'h': 50},
            ]
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

        # 문 그리기
        if self.image2:
            # 아래쪽 문 (삭제 예정)

            dx, dy = game_world.world_to_screen(490, 175)

            self.image2.clip_composite_draw(0, 40, 50, 52, 0, 'v', dx, dy - 20, 120, 120)
            self.image2.clip_composite_draw(50, 40, 50, 52, 0, 'v', dx + 35, dy - 20, 130, 120)

    def ensure_obstacles(self):
        # 추후 보스 몬스터 생성 로직이 들어갈 곳
        if self.boss is None:
            # 상단 중앙 쯤에 위치 (맵 중앙 X: 487, 상단 Y: 600 정도)
            self.boss = Boss(487, 600)

            # 보스가 월드에 등록되어 있지 않다면 등록 (레이어 1: 몬스터/아이작 레이어)
        if self.boss not in sum(game_world.world, []):
            game_world.add_object(self.boss, 1)
        pass

    def clear_obstacles(self):
        # 스테이지를 떠날 때 정리할 것들
        if self.boss:
            game_world.remove_object(self.boss)
        pass