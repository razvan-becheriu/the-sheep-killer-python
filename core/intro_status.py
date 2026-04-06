import sdl2
import sdl2.sdlmixer as sdlmixer
from OpenGL.GL import *
from OpenGL.GLU import *

from core.state import BaseStatus
from core.globals import global_vars
from core.ortho import begin_ortho, end_ortho # Import ortho functions
from core.level_status import LevelStatus # Import LevelStatus

class IntroStatus(BaseStatus):
    """
    Represents the introduction screen of the game.
    (Ported from introstatusunit.pas)
    """
    def __init__(self):
        super().__init__()
        self.last_tick = sdl2.SDL_GetTicks()
        self.music = None

    def do_enter(self):
        super().do_enter()
        # Load and play the background module
        self.music = sdlmixer.Mix_LoadMUS(b"media/yeeha.xm")
        if self.music:
            sdlmixer.Mix_PlayMusic(self.music, -1)

    def do_exit(self):
        super().do_exit()
        sdlmixer.Mix_HaltMusic()
        global_vars.media_manager.play_sound('x2')

    def do_loop(self, delta: float):
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        begin_ortho(global_vars.screen_width, global_vars.screen_height)

        # Draw intro screen
        glColor3f(1.0, 1.0, 1.0)
        intro_texture = global_vars.media_manager.get_texture('intro')
        if intro_texture:
            glEnable(GL_TEXTURE_2D)
            intro_texture.bind()
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(0, 0) # Top-Left
            glTexCoord2f(0, 1); glVertex2f(0, global_vars.screen_height) # Bottom-Left
            glTexCoord2f(1, 1); glVertex2f(global_vars.screen_width, global_vars.screen_height) # Bottom-Right
            glTexCoord2f(1, 0); glVertex2f(global_vars.screen_width, 0) # Top-Right
            glEnd()
            glDisable(GL_TEXTURE_2D)
        else:
            # Fallback if texture not loaded
            print("Warning: 'intro' texture not found.")
            glBegin(GL_QUADS)
            glVertex2f(0, 0); glVertex2f(global_vars.screen_width, 0); glVertex2f(global_vars.screen_width, global_vars.screen_height); glVertex2f(0, global_vars.screen_height)
            glEnd()

        end_ortho()

    def key_down(self, event: sdl2.SDL_KeyboardEvent):
        if event.keysym.sym == sdl2.SDLK_SPACE:
            global_vars.state_manager.change_status(LevelStatus(global_vars.game_list)) # Change to LevelStatus
        elif event.keysym.sym == sdl2.SDLK_ESCAPE:
            global_vars.loop_running = False

    def key_up(self, event: sdl2.SDL_KeyboardEvent):
        pass

    def mouse_move(self, event: sdl2.SDL_MouseMotionEvent):
        global_vars.mx, global_vars.my = event.x, event.y