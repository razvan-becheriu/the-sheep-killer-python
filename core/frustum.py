import math
from OpenGL.GL import *

class FrustumCuller:
    def __init__(self):
        # 6 planes, each with 4 coefficients (A, B, C, D)
        self.frustum = [[0.0] * 4 for _ in range(6)]

    def normalize_plane(self, side: int):
        f = self.frustum[side]
        mag = math.sqrt(f[0]**2 + f[1]**2 + f[2]**2)
        if mag != 0:
            self.frustum[side] = [x / mag for x in f]

    def calculate(self):
        proj = glGetFloatv(GL_PROJECTION_MATRIX)
        modl = glGetFloatv(GL_MODELVIEW_MATRIX)

        # PyOpenGL returns 4x4 NumPy arrays if available. 
        # We must flatten them to 1D (16 elements) to match the port's indexing logic.
        if hasattr(proj, 'flatten'):
            proj = proj.flatten()
        if hasattr(modl, 'flatten'):
            modl = modl.flatten()

        clip = [0.0] * 16

        # Combine matrices
        for i in range(4):
            for j in range(4):
                clip[i*4 + j] = (modl[i*4 + 0] * proj[0*4 + j] +
                                 modl[i*4 + 1] * proj[1*4 + j] +
                                 modl[i*4 + 2] * proj[2*4 + j] +
                                 modl[i*4 + 3] * proj[3*4 + j])

        # Right, Left, Bottom, Top, Back, Front planes
        self.frustum[0] = [clip[3]-clip[0], clip[7]-clip[4], clip[11]-clip[8], clip[15]-clip[12]]
        self.frustum[1] = [clip[3]+clip[0], clip[7]+clip[4], clip[11]+clip[8], clip[15]+clip[12]]
        self.frustum[2] = [clip[3]+clip[1], clip[7]+clip[5], clip[11]+clip[9], clip[15]+clip[13]]
        self.frustum[3] = [clip[3]-clip[1], clip[7]-clip[5], clip[11]-clip[9], clip[15]-clip[13]]
        self.frustum[4] = [clip[3]-clip[2], clip[7]-clip[6], clip[11]-clip[10], clip[15]-clip[14]]
        self.frustum[5] = [clip[3]+clip[2], clip[7]+clip[6], clip[11]+clip[10], clip[15]+clip[14]]

        for i in range(6):
            self.normalize_plane(i)

    def is_sphere_within(self, x: float, y: float, z: float, radius: float) -> bool:
        for i in range(6):
            if (self.frustum[i][0] * x + self.frustum[i][1] * y + 
                self.frustum[i][2] * z + self.frustum[i][3]) <= -radius:
                return False
        return True