import math

class Vector2:
    """Simple 2D Vector class (Ported from vector2d.pas)"""
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            self.x, self.y = 1.0, 0.0
        else:
            self.x /= mag
            self.y /= mag

    def rotate(self, angle: float):
        """Rotates the vector by an angle in radians"""
        s, c = math.sin(angle), math.cos(angle)
        nx = self.x * c + self.y * s
        ny = -self.x * s + self.y * c
        return Vector2(nx, ny)

    def get_angle(self) -> float:
        return math.atan2(self.x, self.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)

class Vector3:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x, self.y, self.z = x, y, z
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag; self.y /= mag; self.z /= mag

def get_vector2(x: float, y: float) -> Vector2:
    return Vector2(x, y)

def rotate(v: Vector2, angle: float) -> Vector2:
    """Helper to rotate a vector using the class method."""
    return v.rotate(angle)

def vector_sub(v1: Vector3, v2: Vector3) -> Vector3:
    return Vector3(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def vector_dot(v1: Vector3, v2: Vector3) -> float:
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

def sphereraycollision(ray_origin: Vector3, ray_dir: Vector3, sphere_pos: Vector3, radius: float) -> bool:
    """Ported from msxmath.pas. Checks if a ray hits a sphere."""
    dist = vector_sub(ray_origin, sphere_pos)
    # Ray Direction is assumed to be normalized
    b = ray_dir.x * dist.x + ray_dir.y * dist.y + ray_dir.z * dist.z
    c = dist.x * dist.x + dist.y * dist.y + dist.z * dist.z - radius * radius
    d = b * b - c
    return d >= 0.0

def get_vector3(x: float, y: float, z: float) -> Vector3:
    return Vector3(x, y, z)

def sign(x: float) -> int:
    return (x > 0) - (x < 0)

def interpolate_float(a: float, b: float, value: float) -> float:
    return a + (b - a) * value

def interpolate_vector3(v1: Vector3, v2: Vector3, value: float) -> Vector3:
    return Vector3(
        interpolate_float(v1.x, v2.x, value),
        interpolate_float(v1.y, v2.y, value),
        interpolate_float(v1.z, v2.z, value)
    )

def angle_dist(a: float, b: float) -> float:
    """Calculates the shortest angular distance between two angles (radians)"""
    x = a - b
    y = (math.pi * 2) - a + b
    if abs(x) < abs(y):
        return -x
    return y
