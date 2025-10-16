from pico2d import load_image

from state_machine import StateMachine

class Idle:
    def __init__(self, isaac):
        self.isaac = isaac
        self.frame_counter = 0
    def enter(self,e):
        self.isaac.dir = 0

    def exit(self,e):
        pass
    def do(self):
        self.frame_counter += 1
        if self.frame_counter % 10 == 0:
            self.isaac.frame = (self.isaac.frame + 1) % 2
        pass
    def draw(self):
        # 몸통
        self.isaac.image.clip_draw(0, 850, 40, 30, self.isaac.x, self.isaac.y - 35, 90, 80)
        #머리
        self.isaac.image.clip_draw(0, 900, 40, 35, self.isaac.x, self.isaac.y,90,75)

class Isaac:
    def __init__(self):
        self.x, self.y = 500,300
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
