import sdl2

class KeyState:
    """Centralized keyboard state tracker (Ported from keyboardunit.pas)"""
    def __init__(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.tab = False
        self.ctrl = False
        self.shift = False
        self.space = False

    def reset(self):
        self.left = self.right = self.up = self.down = self.space = False
        self.tab = self.ctrl = self.shift = False

    def process_key_event(self, symbol: int, is_down: bool):
        if symbol == sdl2.SDLK_RIGHT:
            self.right = is_down
        elif symbol == sdl2.SDLK_LEFT:
            self.left = is_down
        elif symbol == sdl2.SDLK_UP:
            self.up = is_down
        elif symbol == sdl2.SDLK_DOWN:
            self.down = is_down
        elif symbol == sdl2.SDLK_TAB:
            self.tab = is_down
        elif symbol in (sdl2.SDLK_RCTRL, sdl2.SDLK_LCTRL):
            self.ctrl = is_down
        elif symbol in (sdl2.SDLK_RSHIFT, sdl2.SDLK_LSHIFT):
            self.shift = is_down
        elif symbol == sdl2.SDLK_SPACE:
            self.space = is_down