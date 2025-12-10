from pico2d import *
import game_framework
import game_world
import title_mode # 다시 타이틀로 돌아가려면 필요
import play_mode
from stage_1 import Stage_1


def init():
    global image
    try:
        image = load_image('resource/game_clear.png')
    except:
        image = None

def finish():
    global image
    del image

def update():
    pass

def draw():
    clear_canvas()
    if image:
        image.draw(500, 400, 1000, 800)
    else:
        # 이미지가 없을 경우 대체 화면
        pass
    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            # 스페이스바를 누르면 타이틀로 돌아가거나 종료
            play_mode._remove_projectiles()
            game_world.clear()
            stage_index = 1
            stage = Stage_1()
            import common
            common.stage = stage
            game_framework.change_mode(title_mode)