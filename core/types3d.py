import math
from typing import List, Any, Optional
from xml.etree import ElementTree as ET

from core.logger import log

# Constants from types3d.pas
EPSILON = 1e-12

# --- Types from types3d.pas ---
class Vertex:
    def __init__(self, x=0.0, y=0.0, z=0.0, nx=0.0, ny=0.0, nz=0.0, tu=0.0, tv=0.0):
        self.x, self.y, self.z = x, y, z
        self.nx, self.ny, self.nz = nx, ny, nz
        self.tu, self.tv = tu, tv

    def __repr__(self):
        return f"Vertex(pos=({self.x},{self.y},{self.z}), normal=({self.nx},{self.ny},{self.nz}), uv=({self.tu},{self.tv}))"

class UV:
    def __init__(self, u=0.0, v=0.0):
        self.u, self.v = u, v

    def __repr__(self):
        return f"UV({self.u},{self.v})"

class Face:
    def __init__(self, p1=0, p2=0, p3=0, nx=0.0, ny=0.0, nz=0.0, uv1=None, uv2=None, uv3=None, smooth=True):
        self.points = [p1, p2, p3] # 0-indexed vertex indices
        self.nx, self.ny, self.nz = nx, ny, nz
        self.uv = [uv1 if uv1 else UV(), uv2 if uv2 else UV(), uv3 if uv3 else UV()]
        self.smooth = smooth

    def __repr__(self):
        return f"Face(points={self.points}, normal=({self.nx},{self.ny},{self.nz}), uv={self.uv}, smooth={self.smooth})"

# --- TMesh from meshunit.pas ---
class Mesh:
    def __init__(self):
        self.name = ""
        self.radius = 0.0
        self.user_data = 0
        self.vertices: List[Vertex] = []
        self.faces: List[Face] = []

    @property
    def num_faces(self) -> int:
        return len(self.faces)

    @property
    def num_vertices(self) -> int:
        return len(self.vertices)

    def calculate_normals(self):
        # Porting CalcolateNormals from meshunit.pas
        # Face normals
        for i, face in enumerate(self.faces):
            v0 = self.vertices[face.points[0]]
            v1 = self.vertices[face.points[1]]
            v2 = self.vertices[face.points[2]]

            x0, y0, z0 = v0.x, v0.y, v0.z
            x1, y1, z1 = v1.x, v1.y, v1.z
            x2, y2, z2 = v2.x, v2.y, v2.z

            x = (y1 - y0) * (z2 - z0) - (y2 - y0) * (z1 - z0)
            y = (z1 - z0) * (x2 - x0) - (z2 - z0) * (x1 - x0)
            z = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)

            s = math.sqrt(x*x + y*y + z*z)
            if s != 0:
                face.nx, face.ny, face.nz = x / s, y / s, z / s
            else:
                face.nx, face.ny, face.nz = 0.0, 0.0, 0.0 # Degenerate face

        # Vertex normals
        # We use a dictionary to group vertices by position to handle hard edges/unshared vertices
        pos_to_normals = {}

        for i, face in enumerate(self.faces):
            if not face: continue
            for pt_idx in face.points:
                v = self.vertices[pt_idx]
                if not v: continue
                pos = (round(v.x, 4), round(v.y, 4), round(v.z, 4)) # Use rounded position for grouping
                if pos not in pos_to_normals:
                    pos_to_normals[pos] = [0.0, 0.0, 0.0, 0] # nx, ny, nz, count
                
                # Accumulate face normal into this position's bucket
                pos_to_normals[pos][0] += face.nx
                pos_to_normals[pos][1] += face.ny
                pos_to_normals[pos][2] += face.nz
                pos_to_normals[pos][3] += 1

        # Assign and normalize the averaged normals back to vertices
        for i, vertex in enumerate(self.vertices):
            if vertex:
                pos = (round(vertex.x, 4), round(vertex.y, 4), round(vertex.z, 4))
                if pos in pos_to_normals:
                    nx, ny, nz, count = pos_to_normals[pos]
                    avg_nx, avg_ny, avg_nz = nx / count, ny / count, nz / count
                    mag = math.sqrt(avg_nx**2 + avg_ny**2 + avg_nz**2)
                    if mag > 0:
                        vertex.nx, vertex.ny, vertex.nz = avg_nx / mag, avg_ny / mag, avg_nz / mag
                    else:
                        vertex.nx, vertex.ny, vertex.nz = 0.0, 1.0, 0.0

    def translate(self, x: float, y: float, z: float):
        for vertex in self.vertices:
            vertex.x += x
            vertex.y += y
            vertex.z += z

    def scale(self, factor: float):
        for vertex in self.vertices:
            vertex.x *= factor
            vertex.y *= factor
            vertex.z *= factor

    def _load_from_xml_node(self, xml_node: ET.Element):
        self.name = xml_node.findtext('NAME', default="")

        points_node = xml_node.find('POINTS')
        if points_node:
            for v_node in points_node.findall('VERTEX'):
                idx = int(v_node.get('id'))
                x = float(v_node.findtext('X', '0.0'))
                y = float(v_node.findtext('Y', '0.0'))
                z = float(v_node.findtext('Z', '0.0'))
                nx = float(v_node.findtext('NX', '0.0'))
                ny = float(v_node.findtext('NY', '0.0'))
                nz = float(v_node.findtext('NZ', '0.0'))
                tu = float(v_node.findtext('U', '0.0'))
                tv = float(v_node.findtext('V', '0.0'))
                # Ensure vertices list is large enough to handle the index
                while len(self.vertices) <= idx:
                    self.vertices.append(None)
                self.vertices[idx] = Vertex(x, y, z, nx, ny, nz, tu, tv)

        faces_node = xml_node.find('FACES')
        if faces_node:
            for f_node in faces_node.findall('FACE'):
                idx = int(f_node.get('id'))
                p1 = int(f_node.findtext('A', '0'))
                p2 = int(f_node.findtext('B', '0'))
                p3 = int(f_node.findtext('C', '0'))
                nx = float(f_node.findtext('NX', '0.0'))
                ny = float(f_node.findtext('NY', '0.0'))
                nz = float(f_node.findtext('NZ', '0.0'))
                
                # Pascal logic: anything that isn't '0' is considered smooth/true
                smooth_val = f_node.findtext('SMOOTH', '1').strip().lower()
                smooth = smooth_val != '0' and smooth_val != 'false'

                uv1 = UV(float(f_node.findtext('AU', '0.0')), float(f_node.findtext('AV', '0.0')))
                uv2 = UV(float(f_node.findtext('BU', '0.0')), float(f_node.findtext('BV', '0.0')))
                uv3 = UV(float(f_node.findtext('CU', '0.0')), float(f_node.findtext('CV', '0.0')))

                while len(self.faces) <= idx:
                    self.faces.append(None)
                self.faces[idx] = Face(p1, p2, p3, nx, ny, nz, uv1, uv2, uv3, smooth)

    def load_from_file(self, filename: str) -> bool:
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            self._load_from_xml_node(root)
            self.calculate_normals() # Ensure smooth shading data is generated
            log.info(f"Successfully parsed mesh: {filename}")
            return True
        except ET.ParseError as e:
            log.error(f"Error parsing XML mesh file {filename}: {e}")
            return False
        except FileNotFoundError:
            log.error(f"Mesh file not found: {filename}")
            # Optionally, create a dummy mesh here to prevent further errors
            return False

    def load_from_stream(self, stream: Any) -> bool:
        try:
            tree = ET.parse(stream)
            root = tree.getroot()
            self._load_from_xml_node(root)
            return True
        except ET.ParseError as e:
            print(f"Error parsing XML stream: {e}")
            return False

    def get_bounding_sphere_radius(self) -> float:
        if self.radius == 0:
            self._calculate_bounding_sphere_radius()
        return self.radius

    def _calculate_bounding_sphere_radius(self):
        self.radius = 0.0
        for vertex in self.vertices:
            if vertex:
                r = math.sqrt(vertex.x**2 + vertex.y**2 + vertex.z**2)
                if r > self.radius:
                    self.radius = r

    def draw(self):
        raise NotImplementedError("Draw method must be implemented by a GLMesh equivalent.")