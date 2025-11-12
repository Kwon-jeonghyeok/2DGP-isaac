from pico2d import *
import game_framework
import game_world
import title_mode


from isaac import Isaac
from stage_1 import Stage_1
from stage_2 import Stage_2

isaac =None
stage = None
Stage = 1
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
    global isaac
    global stage

    stage = Stage_1()
    game_world.add_object(stage,0)


    isaac = Isaac()
    game_world.add_object(isaac,1)


def update():
    game_world.update()
    global Stage
    global stage
    global isaac
    if isaac.y > 720 and Stage ==1:
        game_world.remove_object(stage)
        stage = Stage_2()
        game_world.add_object(stage,0)
        isaac.y = 70


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