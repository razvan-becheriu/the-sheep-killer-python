import sys
import os
from typing import Optional
import ctypes

# Add the project root to sys.path to allow importing 'core'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
try:
    import sdl2
    import sdl2.ext
    import sdl2.sdlimage
    import sdl2.sdlmixer as sdlmixer
except ImportError:
    print("Error: PySDL2 not found. Run 'pip install PySDL2 pysdl2-dll'")
    sys.exit(1)

from OpenGL.GL import *
from OpenGL.GLU import *

from core.globals import global_vars
from core.ortho import begin_ortho, end_ortho
from core.game import BaseList # Import BaseList here
from core.state import StateManager
from core.media import MediaManager
from core.input import KeyState
from core.intro_status import IntroStatus

class TheSheepKiller:
    def __init__(self):
        # self.state_manager = StateManager() # Moved to global_vars
        self.width = 1920
        self.height = 1080
        
        # self.game_list: Optional[BaseList] = None # Moved to global_vars
    def init_systems(self):
        global_vars.game_list = BaseList() # Initialize game_list in globals
        global_vars.media_manager = MediaManager()
        global_vars.state_manager = StateManager() # Initialize state_manager in globals
        global_vars.keystate = KeyState()
        global_vars.screen_width = self.width
        global_vars.screen_height = self.height
        
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_AUDIO | sdl2.SDL_INIT_JOYSTICK)
        sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_PNG) # Initialize SDL_image for PNG loading
        
        # Initialize SDL_mixer (44.1kHz, 16-bit, Stereo, 1024 byte chunks)
        if sdlmixer.Mix_OpenAudio(44100, sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024) < 0:
            print(f"SDL_mixer could not initialize! Error: {sdlmixer.Mix_GetError()}")
        sdlmixer.Mix_AllocateChannels(16)
        
        # Create Window
        flags = sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP

        global_vars.window = sdl2.SDL_CreateWindow(
            b"The Sheep Killer!",
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            self.width, self.height, 
            flags
        )
        
        global_vars.gl_context = sdl2.SDL_GL_CreateContext(global_vars.window)
        if not global_vars.gl_context:
            print(f"Failed to create GL context: {sdl2.SDL_GetError()}")
            return
            
        sdl2.SDL_GL_MakeCurrent(global_vars.window, global_vars.gl_context)
        
        # Get actual pixel dimensions for OpenGL (Fixes High-DPI/Fullscreen corner issue)
        dw, dh = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GL_GetDrawableSize(global_vars.window, dw, dh)
        global_vars.screen_width, global_vars.screen_height = dw.value, dh.value

        # OpenGL Setup (Ported from TProg::initGl)
        glMatrixMode(GL_MODELVIEW)

        # Set Viewport and Perspective Projection
        glViewport(0, 0, dw.value, dh.value)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, dw.value / dh.value, 0.1, 500.0)
        glMatrixMode(GL_MODELVIEW)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.7, 1.0, 1.0, 0.0)
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK) # Still cull back faces
        # Models from the Pascal version/older exporters usually use Clockwise winding
        glFrontFace(GL_CCW) 
        
        glEnable(GL_MULTISAMPLE)
        
        # Smoothing and Normal setup
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE) # Fixes lighting on scaled models
        
        # High quality hints
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        color = [1.0, 1.0, 1.0, 1.0]
        glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
        glMaterialfv(GL_FRONT, GL_AMBIENT, color)
        
        # Depth Buffer Setup
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        
        # Lighting setup
        glDisable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])
        glLightfv(GL_LIGHT0, GL_POSITION, [128.0, 200.0, 128.0, 1.0])
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Load standard game assets
        global_vars.media_manager.load_game_assets()

        # Draw Loading Screen
        # The loading screen is drawn once here to show progress
        self.draw_loading_screen()

        # Initialize game entities and models immediately
        global_vars.game_list.initialize_models(global_vars.media_manager)
        global_vars.game_list.restart() # This sets level to 1

        # IntroStatus, LevelStatus, MainStatus, GameOverStatus will be created as classes
        # For now, let's just set IntroStatus as the initial state.
        # We need to pass the game_list to MainStatus when it's created.
        # global_vars.main_status = MainStatus(global_vars.game_list) # Will be created by LevelStatus
        # global_vars.level_status = LevelStatus(global_vars.game_list) # Will be created by IntroStatus

        # Placeholder for actual state classes
        # The IntroStatus is created here, but the actual game_list is passed to LevelStatus
        self.intro_status = IntroStatus() # This is still needed for the initial state instance
        global_vars.state_manager.change_status(self.intro_status)

    def draw_loading_screen(self):
        """Draws the loading screen once during initialization."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        load_tex = global_vars.media_manager.get_texture('loading')
        if load_tex:
            sw, sh = global_vars.screen_width, global_vars.screen_height
            # Scale the 256x256 loading sprite relative to screen height
            scale = sh / 600.0
            size = 256 * scale
            x1, y1 = (sw - size) / 2, (sh - size) / 2
            x2, y2 = x1 + size, y1 + size

            begin_ortho(sw, sh)
            glDisable(GL_LIGHTING) # UI elements must not be affected by 3D lighting
            glColor3f(1, 1, 1)
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            load_tex.bind()
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x1, y1)
            glTexCoord2f(0, 1); glVertex2f(x1, y2)
            glTexCoord2f(1, 1); glVertex2f(x2, y2)
            glTexCoord2f(1, 0); glVertex2f(x2, y1)
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            end_ortho()
            glEnable(GL_LIGHTING) # RE-ENABLE lighting after drawing UI/Loading screen
        sdl2.SDL_GL_SwapWindow(global_vars.window)

    def main_loop(self):
        event = sdl2.SDL_Event()
        last_tick = sdl2.SDL_GetTicks()

        while global_vars.loop_running:
            while sdl2.SDL_PollEvent(event):
                if event.type == sdl2.SDL_QUIT:
                    global_vars.loop_running = False
                
                # Input Dispatch
                status = global_vars.state_manager.active_status
                if status:
                    # Fullscreen toggle: Alt + Enter
                    if event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_RETURN:
                        if event.key.keysym.mod & (sdl2.KMOD_LALT | sdl2.KMOD_RALT):
                            win_flags = sdl2.SDL_GetWindowFlags(global_vars.window)
                            if win_flags & sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP:
                                sdl2.SDL_SetWindowFullscreen(global_vars.window, 0)
                            else:
                                sdl2.SDL_SetWindowFullscreen(global_vars.window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
                            
                            # Update globals with actual pixel dimensions
                            dw, dh = ctypes.c_int(), ctypes.c_int()
                            sdl2.SDL_GL_GetDrawableSize(global_vars.window, dw, dh)
                            global_vars.screen_width, global_vars.screen_height = dw.value, dh.value
                            glViewport(0, 0, dw.value, dh.value)
                            
                            # Update 3D perspective for new aspect ratio
                            glMatrixMode(GL_PROJECTION)
                            glLoadIdentity()
                            gluPerspective(45.0, dw.value / dh.value, 0.1, 500.0)
                            glMatrixMode(GL_MODELVIEW)

                    if event.type == sdl2.SDL_KEYDOWN:
                        global_vars.keystate.process_key_event(event.key.keysym.sym, True)
                        status.key_down(event.key)
                    elif event.type == sdl2.SDL_KEYUP:
                        # Update global mouse coordinates (from MouseMoveEvent in Pascal)
                        # This is a bit out of place in KEYUP, but matches Pascal's global.mx/my update logic
                        global_vars.keystate.process_key_event(event.key.keysym.sym, False)
                        status.key_up(event.key)
                    elif event.type == sdl2.SDL_MOUSEMOTION:
                        status.mouse_move(event.motion)

            # Timing
            current_tick = sdl2.SDL_GetTicks()
            delta = (current_tick - last_tick) / 1000.0
            last_tick = current_tick

            # Update and Render
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            global_vars.state_manager.update(delta)
            
            sdl2.SDL_GL_SwapWindow(global_vars.window)
            sdl2.SDL_Delay(1)

    def cleanup(self):
        sdlmixer.Mix_CloseAudio()
        sdl2.SDL_GL_DeleteContext(global_vars.gl_context)
        sdl2.SDL_DestroyWindow(global_vars.window)
        sdl2.SDL_Quit()

if __name__ == "__main__":
    app = TheSheepKiller()
    try:
        app.init_systems()
        app.main_loop()
    finally:
        app.cleanup()
