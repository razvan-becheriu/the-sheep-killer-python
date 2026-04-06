import sdl2

class BaseStatus:
    """Equivalent to TEventListener in Pascal"""
    def __init__(self):
        self.active = False

    def do_enter(self):
        self.active = True

    def do_exit(self):
        self.active = False

    def do_loop(self, delta: float):
        pass

    def key_down(self, event: sdl2.SDL_KeyboardEvent):
        pass

    def key_up(self, event: sdl2.SDL_KeyboardEvent):
        pass

    def mouse_move(self, event: sdl2.SDL_MouseMotionEvent):
        pass

class StateManager:
    def __init__(self):
        self.active_status: BaseStatus = None

    def change_status(self, new_status: BaseStatus):
        if self.active_status:
            self.active_status.do_exit()
        
        self.active_status = new_status
        if self.active_status:
            self.active_status.do_enter()

    def update(self, delta: float):
        if self.active_status and self.active_status.active:
            self.active_status.do_loop(delta)