from OpenGL.GL import *
from core.globals import global_vars

# Assuming a fixed character width and height for the font.png
# The font.png seems to have 16x8 characters, each 8x8 pixels.
# Let's assume FONT_CHAR_WIDTH = 8, FONT_CHAR_HEIGHT = 8, and the texture is 128x128 (16*8 x 16*8)
FONT_CHAR_WIDTH = 8
FONT_CHAR_HEIGHT = 8
FONT_TEXTURE_WIDTH = 128
FONT_TEXTURE_HEIGHT = 128

# Constants for 'numbers.png' (from fontunit.pas)
RACE_CHAR_WIDTH = 32
RACE_CHAR_HEIGHT = 64
RACE_TEXTURE_WIDTH = 256
RACE_TEXTURE_HEIGHT = 256 # Asset is sampled as 256px high to isolate 32px rows

def draw_char(x: int, y: int, char_code: int, scale: float = 1.0):
    """Draws a single character from the font texture (font.png)."""
    if char_code < 32 or char_code > 126: # ASCII range for printable characters
        return

    char_index = char_code - 32 # ' ' is the first character in the texture
    
    # Calculate texture coordinates
    chars_per_row = FONT_TEXTURE_WIDTH // FONT_CHAR_WIDTH
    tx = (char_index % chars_per_row) * FONT_CHAR_WIDTH / FONT_TEXTURE_WIDTH
    ty = (char_index // chars_per_row) * FONT_CHAR_HEIGHT / FONT_TEXTURE_HEIGHT + 0.5 # Pascal's font has offset
    tw = FONT_CHAR_WIDTH / FONT_TEXTURE_WIDTH
    th = FONT_CHAR_HEIGHT / FONT_TEXTURE_HEIGHT

    # Calculate vertex coordinates
    width = FONT_CHAR_WIDTH * scale
    height = FONT_CHAR_HEIGHT * scale

    glBegin(GL_QUADS)
    glTexCoord2f(tx, ty); glVertex2f(x, y)
    glTexCoord2f(tx, ty + th); glVertex2f(x, y + height)
    glTexCoord2f(tx + tw, ty + th); glVertex2f(x + width, y + height)
    glTexCoord2f(tx + tw, ty); glVertex2f(x + width, y)
    glEnd()

def draw_string(x: int, y: int, text: str, scale: float = 1.0):
    """Draws a string using the font texture (font.png)."""
    font_texture = global_vars.media_manager.get_texture('font')
    if font_texture:
        font_texture.bind()
        glColor3f(0.0, 0.0, 0.0) # Text color is black
        current_x = x
        for char in text:
            draw_char(current_x, y, ord(char), scale)
            current_x += int(FONT_CHAR_WIDTH * scale)
        glColor3f(1.0, 1.0, 1.0) # Reset color to white after drawing text

def draw_race_char(x: int, y: int, char_code: int, scale: float = 1.0):
    """Draws a single character from the numbers texture (numbers.png)."""
    if char_code < 48 or char_code > 58: # ASCII '0'-'9' and ':'
        return

    char_index = char_code - 48 # '0' is the first character in the texture
    
    # Calculate texture coordinates
    chars_per_row = 8 # 8 characters per row (0-7) in numbers.png
    tx = (char_index % chars_per_row) * RACE_CHAR_WIDTH / RACE_TEXTURE_WIDTH
    ty = (char_index // chars_per_row) * RACE_CHAR_HEIGHT / RACE_TEXTURE_HEIGHT
    tw = RACE_CHAR_WIDTH / RACE_TEXTURE_WIDTH
    th = RACE_CHAR_HEIGHT / RACE_TEXTURE_HEIGHT

    # Calculate vertex coordinates
    width = RACE_CHAR_WIDTH * scale
    height = RACE_CHAR_HEIGHT * scale

    glBegin(GL_QUADS)
    glTexCoord2f(tx, ty); glVertex2f(x, y)
    glTexCoord2f(tx, ty + th); glVertex2f(x, y + height)
    glTexCoord2f(tx + tw, ty + th); glVertex2f(x + width, y + height)
    glTexCoord2f(tx + tw, ty); glVertex2f(x + width, y)
    glEnd()

def draw_race_string(x: int, y: int, text: str, scale: float = 1.0):
    """Draws a string using the numbers texture (numbers.png)."""
    numbers_texture = global_vars.media_manager.get_texture('numbers')
    if numbers_texture:
        numbers_texture.bind()
        glColor3f(1.0, 1.0, 1.0) # Text color is white for race string
        current_x = x
        for char in text:
            draw_race_char(current_x, y, ord(char), scale)
            current_x += int(RACE_CHAR_WIDTH * scale)