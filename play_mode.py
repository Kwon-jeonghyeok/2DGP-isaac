from pico2d import *
import game_framework
import game_world
import title_mode


from isaac import Isaac
from stage_1 import Stage_1
from stage_2 import Stage_2
from host import Host
from stage_3 import Stage_3

isaac =None
stage = None
host = None
stage_index = 1
def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            # isaac이 아직 생성되지 않았을 수 있으므로 안전 검사
            if isaac is not None:
                isaac.handle_event(event)

def init():
    global isaac, stage, stage_index, host

    stage = Stage_1()
    game_world.add_object(stage,0)

    #host = Host()
    host = [Host() for i in range(3)]
    isaac = Isaac()
    game_world.add_object(isaac,2)
    stage_index = 1

    game_world.add_collision_pair('isaac:host', isaac, None)
def _remove_projectiles():
    for layer in list(game_world.world):
        for o in list(layer):
            if o is None:
                continue
            name = o.__class__.__name__
            if name in ('Tear', 'HostBullet'):
                try:
                    game_world.remove_object(o)
                except Exception:
                    # 이미 제거되었거나 다른 스레드 문제 등 무시
                    pass


def update():
    global stage, stage_index, isaac, host

    # 안전 검사
    if isaac is None or stage is None:
        return

    # 모든 객체 업데이트
    game_world.update()

    # 맵 경계 적용
    bounds = stage.get_map_bounds()
    isaac.apply_map_bounds(bounds)

    vp_w = game_world.camera.get('w',1000.0)
    vp_h = game_world.camera.get('h',800.0)



    left = bounds.get('map_left', -1e9)
    right = bounds.get('map_right', 1e9)
    bottom = bounds.get('map_bottom', -1e9)
    top = bounds.get('map_top', 1e9)
    cam_x = isaac.x - vp_w / 2.0
    cam_y = isaac.y - vp_h / 2.0

    map_w = right - left
    map_h = top - bottom
    # 카메라의 x는 맵의 좌/우 범위에 따라 제한
    # 맵이 뷰포트보다 좁으면 맵을 뷰포트 안에서 가운데로 정렬
    if map_w <= vp_w:
        cam_x = left + (map_w - vp_w) / 2.0
    else:
        cam_x = max(left, min(cam_x, right - vp_w))

    if map_h <= vp_h:
        cam_y = bottom + (map_h - vp_h) / 2.0
    else:
        cam_y = max(bottom, min(cam_y, top - vp_h))

    game_world.camera['x'] = cam_x
    game_world.camera['y'] = cam_y

    # 충돌 처리
    game_world.handle_collision()



    # 스테이지 전환
    if isaac.y > 750 and stage_index == 1:
        # 기존 스테이지 제거 및 새 스테이지 추가
        _remove_projectiles()
        try:
            game_world.remove_object(stage)
        except ValueError:
            pass
        stage = Stage_2()
        game_world.add_object(stage, 0)
        stage_index = 2


        for h in host:
            game_world.add_object(h,1)
            game_world.add_collision_pair('isaac:host',None,h)
            game_world.add_collision_pair('host:tear', h, None)

        # 플레이어 재배치
        isaac.y = 175
        #isaac.take_damage(1)  # 체력 감소 예시



    if isaac.y < 125 and stage_index == 2:
        # 기존 스테이지 제거 및 새 스테이지 추가
        _remove_projectiles()
        try:
            game_world.remove_object(stage)
            for h in host:
                game_world.remove_object(h)
        except ValueError:
            pass
        stage = Stage_1()
        game_world.add_object(stage, 0)
        stage_index = 1
        # 플레이어 재배치
        isaac.y = 700
    if isaac.y > 750 and stage_index == 2:
        # 기존 스테이지 제거 및 새 스테이지 추가
        _remove_projectiles()
        try:
            game_world.remove_object(stage)
            for h in host:
                game_world.remove_object(h)
        except ValueError:
            pass
        stage = Stage_3()
        game_world.add_object(stage, 0)
        stage_index = 3
        # 플레이어 재배치
        isaac.y = 175
    if isaac.y < 125 and stage_index == 3:
        # 기존 스테이지 제거 및 새 스테이지 추가
        _remove_projectiles()
        try:
            game_world.remove_object(stage)
        except ValueError:
            pass
        stage = Stage_2()
        game_world.add_object(stage, 0)
        stage_index = 2

        for h in host:
            game_world.add_object(h,1)
            game_world.add_collision_pair('iddsaac:host',None,h)
            game_world.add_collision_pair('host:tear', h, None)

        # 플레이어 재배치
        isaac.y = 700


    if isaac.hp <=0:
        _remove_projectiles()
        game_world.clear()
        stage_index = 1
        stage = Stage_1()
        game_framework.change_mode(title_mode)

    pass


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()
    pass

def pause(): pass
def resume(): pass