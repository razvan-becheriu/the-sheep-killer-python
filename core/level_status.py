import sdl2
from OpenGL.GL import *
from OpenGL.GLU import *

from core.state import BaseStatus
from core.globals import global_vars
from core.font_renderer import draw_string, draw_race_string
from core.ortho import begin_ortho, end_ortho
from core.renderer import draw_realtime_model
from core.animation import AnimationHandler
from core.model import RealTimeModel
from core.main_status import MainStatus # Import MainStatus for transition

class LevelStatus(BaseStatus):
    """
    Represents the intermission screen between levels.
    (Ported from levelstatusunit.pas)
    """
    def __init__(self, game_list):
        super().__init__()
        self.game_list = game_list
        self.intermission_model = None
        self.intermission_anim = None
        self.last_tick = sdl2.SDL_GetTicks()

    def do_enter(self):
        super().do_enter()
        self.starttime = sdl2.SDL_GetTicks() # Initialize start time
            
        # Setup Viking for intermission screen
        # Use the already loaded model from the game list
        self.intermission_anim = AnimationHandler(self.game_list.anim_viking)
        self.intermission_anim.start(1, 1.0) # Walk animation

    def do_exit(self):
        super().do_exit()

    def do_loop(self, delta: float):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # 3D View for the intermission Viking
        gluLookAt(20, 22, 20, 0, 2, 0, 0, 1, 0)
        
        glEnable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0) # Reset color for model rendering
        glDisable(GL_TEXTURE_2D)

        if self.intermission_anim:
            self.intermission_anim.update(delta)
            self.intermission_anim.interpolate()
            draw_realtime_model(self.intermission_anim.model)

        glDisable(GL_LIGHTING)

        # 2D UI rendering
        sw, sh = global_vars.screen_width, global_vars.screen_height
        uiscale = sh / 768.0
        begin_ortho(sw, sh)

        # Draw the "Level X" and "Press SPACE" header
        # The background 'wri' texture already contains the word 'LEVEL'.
        # We sample the middle section of wri.png for "LEVEL"
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D) # Ensure textures are enabled for this background
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Calculate Banner center (Reference 800x600 coordinates)
        bw, bh = 140 * uiscale, 70 * uiscale
        bx = sw // 2 - 80 * uiscale
        by = 180 * uiscale

        wri_tex = global_vars.media_manager.get_texture('wri')
        if wri_tex:
            glColor3f(1, 1, 1)
            wri_tex.bind()
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0.3);  glVertex2f(bx, by)
            glTexCoord2f(0, 0.65); glVertex2f(bx, by + bh)
            glTexCoord2f(1, 0.65); glVertex2f(bx + bw, by + bh)
            glTexCoord2f(1, 0.3);  glVertex2f(bx + bw, by)
            glEnd()

        draw_race_string(bx + bw + 10 * uiscale, by + 5 * uiscale, str(self.game_list.level), uiscale)
        draw_string(sw // 2 - 100 * uiscale, sh - 64 * uiscale, "Press SPACE to start!", uiscale)

        end_ortho()

    def key_down(self, event: sdl2.SDL_KeyboardEvent):
        if event.keysym.sym == sdl2.SDLK_SPACE:
            # Transition to MainStatus (actual gameplay)
            global_vars.state_manager.change_status(MainStatus(self.game_list))
        elif event.keysym.sym == sdl2.SDLK_ESCAPE:
            global_vars.loop_running = False

    def key_up(self, event: sdl2.SDL_KeyboardEvent):
        pass

    def mouse_move(self, event: sdl2.SDL_MouseMotionEvent):
        global_vars.mx, global_vars.my = event.x, event.y