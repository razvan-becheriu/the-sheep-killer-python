import sdl2
from OpenGL.GL import *
from OpenGL.GLU import *
from core.state import BaseStatus
from core.globals import global_vars
from core.ortho import begin_ortho, end_ortho
from core.font_renderer import draw_string, draw_race_string
from core.highscore import Highscore

class GameOverStatus(BaseStatus):
    def __init__(self, final_score: int):
        super().__init__()
        self.score = final_score
        self.highscore_man = Highscore()
        self.player_name = ""
        self.entering_name = True

    def do_enter(self):
        super().do_enter()
        self.highscore_man.load()
        global_vars.keystate.reset()
        # Enable text input for name entry
        sdl2.SDL_StartTextInput()

    def do_exit(self):
        super().do_exit()
        sdl2.SDL_StopTextInput()
        global_vars.media_manager.play_sound('x2')
        # Restart game logic for next run
        if global_vars.game_list:
            global_vars.game_list.restart()

    def do_loop(self, delta: float):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        sw = global_vars.screen_width
        sh = global_vars.screen_height
        uiscale = sh / 768.0 # Base height reference: 600px

        begin_ortho(sw, sh)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Draw Game Over Background
        go_tex = global_vars.media_manager.get_texture('gameover')
        if go_tex:
            glEnable(GL_TEXTURE_2D) # Enable textures for this background
            glEnable(GL_BLEND) # Enable blending for this background (if alpha)
            glColor3f(1, 1, 1)
            go_tex.bind()
            glBegin(GL_QUADS) # Draw the "GAME OVER" part of the texture
            glTexCoord2f(0, 0); glVertex2f(0, 0)
            glTexCoord2f(1, 0); glVertex2f(global_vars.screen_width, 0)
            glTexCoord2f(1, 0.5); glVertex2f(global_vars.screen_width, global_vars.screen_height / 2) # Sample top half
            glTexCoord2f(0, 0.5); glVertex2f(0, global_vars.screen_height / 2)
            glEnd()

        # Draw Final Score
        draw_race_string(sw // 2 - (len(str(self.score)) * 16 * uiscale), 400 * uiscale, str(self.score), uiscale)

        if self.entering_name:
            draw_string(sw // 2 - 100 * uiscale, 500 * uiscale, "Insert your name!", uiscale)
            # Draw a simple text field representation
            display_name = self.player_name + "_"
            draw_string(sw // 2 - 100 * uiscale, 520 * uiscale, display_name, uiscale)
        else:
            # Draw Highscore List - changed to white for visibility
            glColor3f(1, 1, 1)
            draw_string(sw // 2 - 50 * uiscale, 500 * uiscale, "*HIGHSCORES*", uiscale)
            for i in range(self.highscore_man.count):
                s, n = self.highscore_man.get_entry(i)
                draw_string(sw // 2 - 80 * uiscale, (520 + i * 15) * uiscale, str(s), uiscale)
                draw_string(sw // 2 - 10 * uiscale, (520 + i * 15) * uiscale, n, uiscale)
            
            glColor3f(1, 1, 1)
            draw_string(sw // 2 - 150 * uiscale, sh - 40 * uiscale, "Press SPACE to return to Intro", 0.8 * uiscale)

        end_ortho()

    def key_down(self, event: sdl2.SDL_KeyboardEvent):
        key = event.keysym.sym
        
        if self.entering_name:
            if key == sdl2.SDLK_RETURN:
                if self.player_name.strip():
                    self.highscore_man.add_score(self.score, self.player_name.strip())
                    self.highscore_man.save()
                self.entering_name = False
            elif key == sdl2.SDLK_BACKSPACE:
                self.player_name = self.player_name[:-1]
            else:
                # Basic name entry logic
                char = sdl2.SDL_GetKeyName(key).decode('utf-8')
                if len(char) == 1 and len(self.player_name) < 20:
                    self.player_name += char
        else:
            if key == sdl2.SDLK_SPACE:
                from core.intro_status import IntroStatus
                global_vars.state_manager.change_status(IntroStatus())
            elif key == sdl2.SDLK_ESCAPE:
                global_vars.loop_running = False