from pico2d import *

class stage_1:
    def __init__(self):
        self.image = load_image('C:/Users/jhkwo/OneDrive/gitbub/2DGP-isaac/resourse/rooms/Rooms_Basement-1.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(250, 600,500,400)
        self.image.composite_draw(0,'h',750,600,500,400)
        self.image.composite_draw(0,'v',250,200,500,400)
        self.image.composite_draw(0,'hv',750,200,500,400)
        pass


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
    stage = stage_1()
    world.append(stage)
    pass


open_canvas(1000, 800)
reset_world()

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

while running:
    handle_events()
    update_world()
    render_world()
    delay(0.05)

close_canvas()
