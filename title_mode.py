from pico2d import *
from pico2d import open_canvas, close_canvas
import game_framework
import play_mode
image = None



frame = 0
time_acc = 0.0
FRAME_DELAY = 0.1

def init():
    global image, frame, time_acc
    image = load_image('resource/titlemenu.png')
    frame = 0
    time_acc = 0.0

def finish():
    global image
    del image
def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_SPACE):
            game_framework.change_mode(play_mode)

def draw():
    clear_canvas()
    image.clip_draw(0,270,480,270,500,400,1000,800 )
    image.clip_draw(0, 160, 480, 100, 500, 630, 1000, 240)
    # 두 프레임을 번갈아 그리기
    if frame == 0:
        image.clip_draw(0, 0, 160, 160, 470, 300, 400, 400)
        image.clip_draw(350, 0, 90, 80, 800, 360, 200, 200)
    else:
        image.clip_draw(160, 0, 160, 160, 470, 300, 400, 400)
        image.clip_draw(350, 80, 90, 80, 800, 360, 200, 200)
    update_canvas()

def update():
    global frame, time_acc
    time_acc += game_framework.frame_time
    if time_acc >= FRAME_DELAY:
        frame = (frame + 1) % 2
        time_acc -= FRAME_DELAY

def pause(): pass
def resume(): pass