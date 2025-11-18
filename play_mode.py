from pico2d import *
import game_framework
import game_world
import title_mode


from isaac import Isaac
from stage_1 import Stage_1
from stage_2 import Stage_2
from host import Host
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
    host = [Host() for i in range(5)]
    isaac = Isaac()
    game_world.add_object(isaac,1)
    stage_index = 1

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

    # 충돌 처리
    game_world.handle_collision()



    # 스테이지 전환
    if isaac.y > 750 and stage_index == 1:
        # 기존 스테이지 제거 및 새 스테이지 추가
        try:
            game_world.remove_object(stage)
        except ValueError:
            pass
        stage = Stage_2()
        game_world.add_object(stage, 0)
        stage_index = 2


        for h in host:
            game_world.add_object(h,1)
        # 플레이어 재배치
        isaac.y = 175
        isaac.take_damage(1)  # 체력 감소 예시



    if isaac.y < 125 and stage_index == 2:
        # 기존 스테이지 제거 및 새 스테이지 추가
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