from pico2d import *

from stage_1 import Stage_1


def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global running
    running = True
    global world
    world = []
    stage = Stage_1()
    world.append(stage)
    pass



def update_world():
    for o in world:
        o.update()
    pass

def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()
    pass


open_canvas(1000, 800)
reset_world()

while running:
    handle_events()
    update_world()
    render_world()
    delay(0.05)

close_canvas()
