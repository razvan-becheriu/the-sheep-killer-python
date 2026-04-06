from OpenGL.GL import *
from OpenGL.GLU import *

def begin_ortho(width: float, height: float):
    """
    Sets up an orthographic projection for 2D drawing.
    Equivalent to Pascal's BeginOrtho.
    """
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING) # 2D UI should not be lit by 3D lights
    glDisable(GL_CULL_FACE) # Disable culling for 2D UI
    glMatrixMode(GL_PROJECTION)
    glEnable(GL_TEXTURE_2D) # Enable textures for all 2D drawing (can be disabled by drawing functions then re-enabled)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1) # Note: Pascal uses 0, 100 for near/far, but -1, 1 is common for 2D UI
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def end_ortho():
    """
    Restores the previous projection matrix (usually perspective) and re-enables depth test.
    Equivalent to Pascal's EndOrtho.
    """
    glDisable(GL_TEXTURE_2D) # Restore texture state after 2D drawing
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE) # Re-enable culling for 3D models
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW) # Restore modelview matrix mode
    glLoadIdentity() # Reset modelview matrix
def draw_rectangle_2d(x: float, y: float, w: float, h: float):
    """
    Draws a 2D rectangle in the current orthographic projection.
    Assumes GL_TEXTURE_2D is enabled and a texture is bound.
    """
    glBegin(GL_QUADS)
    # Pascal's Rectangle2d uses GL_TRIANGLE_STRIP, but GL_QUADS is more intuitive for a simple rectangle
    # and achieves the same result with these vertex orders.
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glEnd()