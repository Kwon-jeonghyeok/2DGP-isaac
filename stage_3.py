from pico2d import load_image
import game_world

class Stage_3:
    def __init__(self):
        self.image = load_image('resource/rooms/Rooms_Basement-1.png')
        self.image2 = load_image('resource/objects/Door_1.png')

    def get_map_bounds(self):
        return {
            'map_left': 100,
            'map_right': 1500,
            'map_bottom': 175,
            'map_top': 700,
            'notches': [

                {'x': 1500, 'y': 400, 'w': 50, 'h': 70},
                {'x': 490, 'y': 175, 'w': 50, 'h': 50},
            ]
        }


    def update(self):
        pass

    def draw(self):

        cam_x = game_world.camera['x']
        cam_y = game_world.camera['y']
        # 타일처럼 가로로 여러번 그려서 긴 맵을 표현
        tile_w = 500
        tile_h = 400
        # 시작 타일 인덱스와 끝 인덱스 계산하여 화면에 보이는 타일만 그림
        start_idx = int((cam_x - 0) // tile_w) - 1
        end_idx = int((cam_x + game_world.camera['w']) // tile_w) + 1

        for i in range(start_idx, end_idx + 1):
            world_x = 250 + i * tile_w  # 원래 이미지가 (250,600) 중심이라고 가정
            world_y = 600 if i % 2 == 0 else 200
            screen_x = world_x - cam_x
            screen_y = world_y - cam_y
            # 이미지 변형은 원본 Stage_2와 비슷하게 배치
            self.image.draw(screen_x, screen_y, tile_w, tile_h)

        # 문 등 고정 오브젝트도 월드 좌표에서 카메라 보정
        door_world_x = 500
        door_world_y = 120
        self.image2.clip_composite_draw(0, 40, 50, 52, 0, 'v', door_world_x - cam_x, door_world_y - cam_y, 120, 120)
        self.image2.clip_composite_draw(50, 40, 50, 52, 0, 'v', 465 - cam_x, 120 - cam_y, 130, 120)


        #self.image.draw(250, 600,500,400)
        #self.image.composite_draw(0,'h',750,600,500,400)
        #self.image.composite_draw(0,'v',250,200,500,400)
        #self.image.composite_draw(0,'hv',750,200,500,400)
        #self.image2.clip_composite_draw(0, 40, 50, 52,0,'v' ,500, 120, 120, 120)
        #self.image2.clip_composite_draw(50, 40, 50, 52,0,'v', 465, 120, 130, 120)


        pass
