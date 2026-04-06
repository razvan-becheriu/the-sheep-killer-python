import sdl2
import sdl2.sdlimage as sdlimage
import sdl2.sdlmixer as sdlmixer
from OpenGL.GL import *
import ctypes
import os
from typing import Dict, Optional, Any
from core.glmesh import GLMesh
from core.logger import log
from core.types3d import Mesh # Import base Mesh type from types3d for type hinting

class Texture:
    def __init__(self, name: str, texture_id: int):
        self.name = name
        self.id = texture_id

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)

    def __del__(self):
        # Python's GC might call this after the GL context is gone,
        # so we usually manage cleanup explicitly in a Real game.
        pass

class Sound:
    def __init__(self, name: str, chunk: Any):
        self.name = name
        self.chunk = chunk

    def play(self):
        if self.chunk:
            sdlmixer.Mix_PlayChannel(-1, self.chunk, 0)

class MediaManager:
    """
    Registry for textures, meshes, models, and sounds (Ported from mediamanagerunit.pas)
    """
    def __init__(self):
        self.textures: Dict[str, Texture] = {}
        self.meshes: Dict[str, GLMesh] = {}
        self.models: Dict[str, Any] = {}
        self.sounds: Dict[str, Sound] = {}

    def load_texture(self, name: str, filename: str) -> bool:
        """Loads a texture from file into OpenGL memory"""
        surface = sdlimage.IMG_Load(filename.encode())
        if not surface:
            log.error(f"Failed to load image {filename}: {sdl2.SDL_GetError()}")
            return False

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Determine format
        mode = GL_RGB if surface.contents.format.contents.BytesPerPixel == 3 else GL_RGBA
        
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1) # Ensure correct row alignment
        glTexImage2D(GL_TEXTURE_2D, 0, mode, surface.contents.w, surface.contents.h, 
                     0, mode, GL_UNSIGNED_BYTE, ctypes.c_void_p(surface.contents.pixels))

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self.textures[name] = Texture(name, texture_id)
        log.info(f"Loaded texture: {name} ({filename})")
        sdl2.SDL_FreeSurface(surface)
        return True

    def load_mesh(self, name: str, filename: str) -> bool:
        """Loads a mesh from file into the manager."""
        mesh = GLMesh()
        if not mesh.load_from_file(filename):
            log.error(f"Failed to load mesh: {filename}")
            return False
        self.meshes[name] = mesh
        return True

    def load_all_meshes(self, directory: str):
        """Automatically loads all .mesh files from a directory."""
        if not os.path.exists(directory):
            print(f"Warning: Mesh directory {directory} not found.")
            return
        for filename in os.listdir(directory):
            if filename.endswith(".mesh"):
                mesh_name = os.path.splitext(filename)[0]
                self.load_mesh(mesh_name, os.path.join(directory, filename))

    def load_sound(self, name: str, filename: str) -> bool:
        """Loads a WAV sound file into the manager."""
        chunk = sdlmixer.Mix_LoadWAV(filename.encode())
        if not chunk:
            print(f"Failed to load sound {filename}: {sdlmixer.Mix_GetError()}")
            return False
        self.sounds[name] = Sound(name, chunk)
        print(f"Successfully loaded sound: {name}")
        return True

    def get_texture(self, name: str) -> Optional[Texture]:
        return self.textures.get(name)

    def get_mesh_by_name(self, name: str) -> Optional[GLMesh]:
        return self.meshes.get(name)

    def get_sound(self, name: str) -> Optional[Sound]:
        return self.sounds.get(name)

    def play_sound(self, name: str):
        s = self.get_sound(name)
        if s: s.play()

    def load_game_assets(self):
        """Centralized registry for standard game assets (Ported from mediamanagerunit.pas)"""
        self.load_texture('intro', 'media/intro.png')
        self.load_texture('tile1', 'media/tile1.png')
        self.load_texture('font', 'media/font.png')
        self.load_texture('heart', 'media/heart.png')
        self.load_texture('sheep', 'media/sheep.png')
        self.load_texture('point', 'media/point.png')
        self.load_texture('numbers', 'media/numbers.png')
        self.load_texture('loading', 'media/loading.png')
        self.load_texture('title', 'media/title.png')
        self.load_texture('gameover', 'media/gameover.png')
        self.load_texture('wri', 'media/wri.png')
        self.load_all_meshes('media')
        self.load_sound('x2', 'media/x2.wav')
        self.load_sound('swhoosh0', 'media/swhoosh0.wav')
        self.load_sound('rambite', 'media/rambite.wav')
        self.load_sound('hit0', 'media/hit0.wav')
        self.load_sound('scream', 'media/scream.wav')
        self.load_sound('sheep', 'media/sheep.wav')
        self.load_sound('ramdie', 'media/ramdie.wav')