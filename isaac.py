from pico2d import load_image

from state_machine import StateMachine

class Idle:
    def __init__(self, isaac):
        self.isaac = isaac
    def enter(self,e):
        self.isaac.dir = 0

    def exit(self,e):
        pass
    def do(self):
        self.isaac.frame = (self.isaac.frame + 1) % 2
        pass
    def draw(self):
        #머리
        self.isaac.image.clip_draw(self.isaac.frame * 35, 900, 35, 35, self.isaac.x, self.isaac.y,100,100)
        #몸통
        self.isaac.image.clip_draw(35, 870, 35, 35, self.isaac.x, self.isaac.y-35, 100, 100)

class Isaac:
    def __init__(self):
        self.x, self.y = 400,300
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.image = load_image('C:/Users/jhkwo/OneDrive/gitbub/2DGP-isaac/resourse/isaac.png')

        self.IDLE = Idle(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {}
            }
        )
        pass
    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
    def handle_event(self,event):
        self.state_machine.handle_state_event(('INPUT', event))
