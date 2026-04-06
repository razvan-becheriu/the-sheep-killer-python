import sdl2
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from core.state import BaseStatus
from core.globals import global_vars
from core.font_renderer import draw_string, draw_race_string # Import draw_race_string
from core.ortho import begin_ortho, end_ortho, draw_rectangle_2d
from core.renderer import draw_realtime_model
from core.game import BaseList, TILESIZE, AREASIZE, Tree
from core.math_utils import Vector3, sphereraycollision
from core.frustum import FrustumCuller

def millis_to_string(millis: int) -> str:
    """Formats milliseconds to MM:SS format (Ported from mainstatusunit.pas)."""
    seconds = (millis // 1000) % 60
    minutes = (millis // 1000) // 60
    return f"{minutes:02d}:{seconds:02d}"

class MainStatus(BaseStatus):
    def __init__(self, game_list: BaseList):
        super().__init__()
        self.list = game_list
        self.time_to_end = 0.0
        self.culler = FrustumCuller()
        self.campos = Vector3()

    def do_enter(self):
        super().do_enter()
        self.starttime = sdl2.SDL_GetTicks() # Initialize start time
        self.time_to_end = 0.0
        global_vars.keystate.reset()

    def test_occlusion(self, entity) -> bool:
        """Checks if an entity is blocking the view of the player (Ported from Pascal)."""
        player_pos = Vector3(self.list.player.position.x, self.list.player.modelsize, self.list.player.position.y)
        dist_to_player = (player_pos - self.campos).magnitude()
        tree_pos = Vector3(entity.position.x, entity.modelsize, entity.position.y)
        if (tree_pos - self.campos).magnitude() >= dist_to_player:
            return False
        ray_dir = (player_pos - self.campos)
        ray_dir.normalize()
        return sphereraycollision(self.campos, ray_dir, tree_pos, entity.modelsize)

    def do_loop(self, delta: float):
        if not self.list:
            return

        # Update Logic (Physics and AI)
        self.list.update(delta)
        
        # Check win/loss conditions
        if self.list.num_sheep == 0 or self.list.player.dead:
            self.time_to_end += delta
            
        if self.time_to_end > 5.0:
            if self.list.num_sheep == 0:
                self.list.next_level()
                from core.level_status import LevelStatus
                global_vars.state_manager.change_status(LevelStatus(self.list))
            elif self.list.player.dead:
                from core.game_over_status import GameOverStatus
                global_vars.state_manager.change_status(GameOverStatus(self.list.score))

        # Set up Camera (Follow Player)
        p = self.list.player.position
        
        # 1. First set light in World Space
        glLoadIdentity()
        glLightfv(GL_LIGHT0, GL_POSITION, [128.0, 200.0, 128.0, 1.0])

        self.campos = Vector3(p.x + 20, 20, p.y + 20)
        # 2. Then set the Camera
        gluLookAt(self.campos.x, self.campos.y, self.campos.z, p.x, 0, p.y, 0, 1, 0)
        self.culler.calculate()

        # Render World
        glDisable(GL_BLEND) # Fixes the "broken transparency" for 3D geometry
        glEnable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0) # Reset color to white so lighting and textures work
        glDisable(GL_TEXTURE_2D) # Textures disabled globally before 3D objects (Pascal behavior)

        # Draw the arena
        self.draw_field()
        
        for entity in self.list:
            # Frustum Culling
            if self.culler.is_sphere_within(entity.position.x, 3, entity.position.y, 3):
                entity.anim.interpolate()
                
                glPushMatrix()
                glTranslatef(entity.position.x, 0, entity.position.y)
                glRotatef(entity.angle * 57.2958, 0, 1, 0)
                
                # Occlusion Transparency (applied to any entity blocking the view)
                if entity != self.list.player and self.test_occlusion(entity):
                    glEnable(GL_BLEND)
                    glBlendFunc(GL_SRC_COLOR, GL_DST_COLOR)
                    glDepthMask(GL_FALSE)
                    draw_realtime_model(entity.anim.model)
                    glDepthMask(GL_TRUE)
                    glDisable(GL_BLEND)
                else:
                    draw_realtime_model(entity.anim.model)
                glPopMatrix()
            
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D) # Re-enable textures for 2D UI (Pascal behavior)

        # 2D UI rendering
        begin_ortho(global_vars.screen_width, global_vars.screen_height)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor3f(1.0, 1.0, 1.0) # Reset color
        
        # Draw FPS and Time (from Pascal)
        draw_string(10, 10, f"FPS: {int(1/delta)}")
        draw_string(100, 10, f"TIME: {millis_to_string(sdl2.SDL_GetTicks() - self.starttime)}")

        # Calculate dynamic positions based on current screen height
        sh = global_vars.screen_height

        # Draw Title Sprite
        title_tex = global_vars.media_manager.get_texture('title')
        if title_tex:
            glColor3f(1.0, 1.0, 1.0) # Reset color for title
            title_tex.bind()
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(0, 0)   # Top-Left
            glTexCoord2f(1, 0); glVertex2f(200, 0) # Top-Right
            glTexCoord2f(1, 1); glVertex2f(200, 200) # Bottom-Right
            glTexCoord2f(0, 1); glVertex2f(0, 200) # Bottom-Left
            glEnd()

        # Draw UI sprites and text stats
        heart_texture = global_vars.media_manager.get_texture('heart')
        if heart_texture:
            glColor3f(1.0, 1.0, 1.0)
            heart_texture.bind()
            draw_rectangle_2d(0, sh - 120, 32, 32)
            draw_race_string(40, sh - 120, str(self.list.player.life), 0.5)

        sheep_texture = global_vars.media_manager.get_texture('sheep')
        if sheep_texture:
            glColor3f(1.0, 1.0, 1.0)
            sheep_texture.bind()
            draw_rectangle_2d(0, sh - 80, 32, 32)
            draw_race_string(40, sh - 80, str(self.list.num_sheep), 0.5)

        point_texture = global_vars.media_manager.get_texture('point')
        if point_texture:
            glColor3f(1.0, 1.0, 1.0)
            point_texture.bind()
            draw_rectangle_2d(0, sh - 40, 32, 32)
            draw_race_string(40, sh - 40, str(self.list.score), 0.5)
        
        end_ortho()
    def key_down(self, event: sdl2.SDL_KeyboardEvent):
        if event.keysym.sym == sdl2.SDLK_ESCAPE:
            global_vars.loop_running = False

    def mouse_move(self, event: sdl2.SDL_MouseMotionEvent):
        global_vars.mx, global_vars.my = event.x, event.y
        if self.list and self.list.player:
            center_x = global_vars.screen_width // 2
            center_y = global_vars.screen_height // 2
            # Rotate player to face the mouse cursor
            # Invert Y difference because screen coordinates are top-down
            self.list.player.angle = math.atan2(event.x - center_x, center_y - event.y)

    def key_up(self, event: sdl2.SDL_KeyboardEvent):
        pass # The keystate global already handles this, but we keep it for symmetry

    def _draw_rectangle_3d(self, x, z, w, h):
        """Helper to draw a 3D rectangle on the XZ plane at Y=0."""
        glBegin(GL_TRIANGLE_STRIP)
        glTexCoord2f(0, 0); glVertex3f(x, 0, z)
        glTexCoord2f(0, 1); glVertex3f(x, 0, z + h)
        glTexCoord2f(1, 0); glVertex3f(x + w, 0, z)
        glTexCoord2f(1, 1); glVertex3f(x + w, 0, z + h)
        glEnd()

    def draw_field(self):
        """Draws the ground tiles and fences (XZ plane)."""
        glPushMatrix()
        glTranslatef(0, 0, TILESIZE / 2)
        for _ in range(AREASIZE):
            draw_realtime_model(self.list.anim_fence)
            glTranslatef(0, 0, TILESIZE)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(TILESIZE / 2, 0, 0)
        glRotatef(-90, 0, 1, 0)
        for _ in range(AREASIZE):
            draw_realtime_model(self.list.anim_fence)
            glTranslatef(0, 0, -TILESIZE)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(AREASIZE * TILESIZE, 0, TILESIZE / 2)
        glRotatef(180, 0, 1, 0)
        for _ in range(AREASIZE):
            draw_realtime_model(self.list.anim_fence)
            glTranslatef(0, 0, -TILESIZE)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(TILESIZE / 2, 0, AREASIZE * TILESIZE)
        glRotatef(90, 0, 1, 0)
        for _ in range(AREASIZE):
            draw_realtime_model(self.list.anim_fence)
            glTranslatef(0, 0, TILESIZE)
        glPopMatrix()

        # Draw Ground (textured, no lighting)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0) # Ensure ground isn't tinted black from text
        tile_tex = global_vars.media_manager.get_texture('tile1')
        if tile_tex:
            tile_tex.bind()
        
        for x in range(AREASIZE):
            for y in range(AREASIZE):
                self._draw_rectangle_3d(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)

        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING) # Restore lighting for entities