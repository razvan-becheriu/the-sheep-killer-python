from OpenGL.GL import *
from typing import List
from core.types3d import Mesh, Vertex, Face # Import from new types3d module

class GLMesh(Mesh):
    """
    Implements an OpenGL based Mesh. (Ported from glmeshunit.pas)
    It builds a display list of the mesh if it doesn't have one already.
    """
    def __init__(self):
        super().__init__()
        self._display_list_id: int = 0

    def _build_display_list(self):
        if self._display_list_id != 0:
            return # Already created

        self._display_list_id = glGenLists(1) # Generate a new display list ID
        if self._display_list_id == 0:
            print(f"OpenGL Error: Failed to generate display list for mesh {self.name}")
            return

        glNewList(self._display_list_id, GL_COMPILE)
        self._draw_complete()
        glEndList()

    def _free_display_list(self):
        if self._display_list_id != 0:
            glDeleteLists(self._display_list_id, 1)
            self._display_list_id = 0

    def _draw_complete(self):
        """
        Does the actual drawing of the object (without display list).
        """
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            if not face: continue
            # Set face normal if not smooth shaded
            if not face.smooth:
                glNormal3f(face.nx, face.ny, face.nz)

            for i in range(3): # For each vertex in the face
                vertex_idx = face.points[i]
                if vertex_idx >= len(self.vertices) or self.vertices[vertex_idx] is None: continue
                vertex = self.vertices[vertex_idx]
                uv = face.uv[i]

                glTexCoord2f(uv.u, uv.v)
                # Set vertex normal if smooth shaded
                if face.smooth:
                    glNormal3f(vertex.nx, vertex.ny, vertex.nz)
                glVertex3f(vertex.x, vertex.y, vertex.z)
        glEnd()

    def draw(self):
        """
        Draw the mesh with the display list (eventually building one on the fly).
        """
        if self._display_list_id == 0:
            self._build_display_list()
        if self._display_list_id != 0:
            glCallList(self._display_list_id)
        else:
            print(f"Warning: Attempted to draw mesh {self.name} with invalid display list ID.")

    def __del__(self):
        # In a real application, you'd need more robust GL resource management
        # as __del__ can be called at arbitrary times, potentially after GL context is gone.
        # For this port, it's a direct translation of the Pascal destructor.
        self._free_display_list()