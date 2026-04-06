import math
from typing import List, Dict, Any, Optional
from xml.etree import ElementTree as ET
 
from core.math_utils import Vector2, Vector3, interpolate_vector3, get_vector3
from core.logger import log
from core.media import MediaManager, Texture # Assuming MediaManager and Texture are defined in core.media
from core.types3d import Mesh, Vertex, UV, Face, EPSILON # Import from new types3d module

# --- TTransformation from modelunit.pas ---
class Transformation:
    def __init__(self):
        self.pos = get_vector3(0, 0, 0)
        self.rot = get_vector3(0, 0, 0) # Euler angles in radians
        self.sca = get_vector3(1, 1, 1)

    def set_zero(self):
        self.pos = get_vector3(0, 0, 0)
        self.rot = get_vector3(0, 0, 0)
        self.sca = get_vector3(0, 0, 0) # Note: Pascal sets to 0,0,0, but scale usually defaults to 1,1,1

    def is_zero(self) -> bool:
        return (self.pos == get_vector3(0,0,0) and
                self.rot == get_vector3(0,0,0) and
                self.sca == get_vector3(0,0,0))

    def must_toggle_faces(self) -> bool:
        return (self.sca.x * self.sca.y * self.sca.z) < 0

    def sum(self, other: 'Transformation') -> 'Transformation':
        new_transf = Transformation()
        new_transf.pos = self.pos + other.pos
        new_transf.rot = self.rot + other.rot 
        new_transf.sca = self.sca + other.sca 
        return new_transf

    def clone(self) -> 'Transformation':
        new_transf = Transformation()
        new_transf.pos = get_vector3(self.pos.x, self.pos.y, self.pos.z)
        new_transf.rot = get_vector3(self.rot.x, self.rot.y, self.rot.z)
        new_transf.sca = get_vector3(self.sca.x, self.sca.y, self.sca.z)
        return new_transf

class GraphicElementType:
    NONE = 0
    MESH = 1
    MODEL = 2
    REFERENCE = 3

class GraphicElement:
    def __init__(self, type: int = GraphicElementType.NONE, mesh: Optional[Mesh] = None, model: Any = None, reference: int = 0):
        self.type = type
        self.mesh = mesh
        self.model = model 
        self.reference = reference

class ModelTreeNode:
    def __init__(self, name: str = "node"):
        self.name = name
        self.transf = Transformation()
        self.color = [1.0, 1.0, 1.0] 
        self.graphic_element = GraphicElement()
        self.texture: Optional[Texture] = None
        self.children: List['ModelTreeNode'] = []

    def load(self, xml_node: ET.Element, media_manager: MediaManager) -> bool:
        self.name = xml_node.findtext('NAME', default="").strip()
        
        texture_name = xml_node.findtext('TEXTURE', default="nil").strip()
        if texture_name != "nil":
            self.texture = media_manager.get_texture(texture_name)

        pos_node = xml_node.find('POS')
        if pos_node:
            self.transf.pos = get_vector3(
                float(pos_node.findtext('X', '0.0')),
                float(pos_node.findtext('Y', '0.0')),
                float(pos_node.findtext('Z', '0.0'))
            )
        rot_node = xml_node.find('ROT')
        if rot_node:
            self.transf.rot = get_vector3(
                float(rot_node.findtext('X', '0.0')),
                float(rot_node.findtext('Y', '0.0')),
                float(rot_node.findtext('Z', '0.0'))
            )
        sca_node = xml_node.find('SCA')
        if sca_node:
            self.transf.sca = get_vector3(
                float(sca_node.findtext('X', '1.0')),
                float(sca_node.findtext('Y', '1.0')),
                float(sca_node.findtext('Z', '1.0'))
            )
        
        color_node = xml_node.find('COLOR')
        if color_node:
            self.color[0] = float(color_node.findtext('RED', '255')) / 255.0
            self.color[1] = float(color_node.findtext('GREEN', '255')) / 255.0
            self.color[2] = float(color_node.findtext('BLUE', '255')) / 255.0

        ge_node = xml_node.find('GRAPHICALELEMENT')
        if ge_node:
            ge_type_str = ge_node.findtext('TYPE', 'none').lower()
            if ge_type_str == 'none':
                self.graphic_element.type = GraphicElementType.NONE
            elif ge_type_str == 'mesh':
                self.graphic_element.type = GraphicElementType.MESH
                mesh_name = ge_node.findtext('MESH', '')
                self.graphic_element.mesh = media_manager.get_mesh_by_name(mesh_name)
            elif ge_type_str == 'model':
                self.graphic_element.type = GraphicElementType.MODEL
            elif ge_type_str == 'reference':
                self.graphic_element.type = GraphicElementType.REFERENCE
                self.graphic_element.reference = int(ge_node.findtext('REFERENCE', '0'))

        for child_node_xml in xml_node.findall('NODE'):
            child_node = ModelTreeNode()
            child_node.load(child_node_xml, media_manager)
            self.children.append(child_node)
        return True

    def clone_deep(self) -> 'ModelTreeNode':
        new_node = ModelTreeNode(self.name)
        new_node.transf = self.transf.clone()
        new_node.color = list(self.color) 
        new_node.graphic_element = GraphicElement(self.graphic_element.type, self.graphic_element.mesh, self.graphic_element.model, self.graphic_element.reference)
        new_node.texture = self.texture 
        for child in self.children:
            new_node.children.append(child.clone_deep())
        return new_node

class TransfTreeNode:
    def __init__(self):
        self.transf = Transformation()
        self.children: List['TransfTreeNode'] = []

class PoseItem:
    def __init__(self, moved_node: str = ""):
        self.moved_node = moved_node
        self.diff = Transformation()
        self.diff.set_zero()

    def load(self, xml_node: ET.Element) -> bool:
        self.moved_node = xml_node.findtext('MOVEDNODE', default="").strip()

        pos_node = xml_node.find('POS')
        if pos_node:
            self.diff.pos = get_vector3(
                float(pos_node.findtext('X', '0.0')),
                float(pos_node.findtext('Y', '0.0')),
                float(pos_node.findtext('Z', '0.0'))
            )
        rot_node = xml_node.find('ROT')
        if rot_node:
            self.diff.rot = get_vector3(
                float(rot_node.findtext('X', '0.0')),
                float(rot_node.findtext('Y', '0.0')),
                float(rot_node.findtext('Z', '0.0'))
            )
        sca_node = xml_node.find('SCA')
        if sca_node:
            self.diff.sca = get_vector3(
                float(sca_node.findtext('X', '1.0')),
                float(sca_node.findtext('Y', '1.0')),
                float(sca_node.findtext('Z', '1.0'))
            )
        return True

class Pose:
    def __init__(self, name: str = "A pose"):
        self.name = name
        self.items: List[PoseItem] = []

    def get_transf_for_node(self, node_name: str, create_if_not_found: bool) -> Optional[Transformation]:
        for item in self.items:
            if item.moved_node == node_name:
                return item.diff
        if create_if_not_found:
            new_item = PoseItem(node_name)
            self.items.append(new_item)
            return new_item.diff
        return None

    def load(self, xml_node: ET.Element) -> bool:
        self.name = xml_node.findtext('NAME', default="").strip()
        self.items.clear()
        for item_node_xml in xml_node.findall('POSEITEM'):
            item = PoseItem()
            item.load(item_node_xml)
            self.items.append(item)
        return True

class AnimationKey:
    def __init__(self, pose_name: str = "", time: int = 0, trigger: bool = False):
        self.pose_name = pose_name
        self.time = time
        self.trigger = trigger

    def load(self, xml_node: ET.Element) -> bool:
        self.pose_name = xml_node.findtext('POSENAME', default="").strip()
        self.time = int(xml_node.findtext('TIME', '0'))
        self.trigger = xml_node.findtext('TRIGGER', 'false').lower() == 'true'
        return True

class Animation:
    def __init__(self, name: str = "Animation"):
        self.name = name
        self.keys: List[AnimationKey] = []

    def load(self, xml_node: ET.Element) -> bool:
        self.name = xml_node.findtext('NAME', default="").strip()
        self.keys.clear()
        for key_node_xml in xml_node.findall('ANIMITEM'):
            key = AnimationKey()
            key.load(key_node_xml)
            self.keys.append(key)
        return True

class Model:
    def __init__(self, name: str = "Amodel"):
        self.name = name
        self.root = ModelTreeNode("root")
        self.poses: List[Pose] = []
        self.animations: List[Animation] = []

    def _load_from_xml_node(self, xml_node: ET.Element, media_manager: MediaManager) -> bool:
        self.name = xml_node.findtext('NAME', default="").strip()
        
        root_node_xml = xml_node.find('NODE')
        if root_node_xml:
            self.root = ModelTreeNode()
            self.root.load(root_node_xml, media_manager)
        
        self.poses.clear()
        for pose_node_xml in xml_node.findall('POSE'):
            pose = Pose()
            pose.load(pose_node_xml)
            self.poses.append(pose)

        self.animations.clear()
        for anim_node_xml in xml_node.findall('ANIMATION'):
            anim = Animation()
            anim.load(anim_node_xml)
            self.animations.append(anim)
        return True

    def load_from_file(self, filename: str, media_manager: MediaManager) -> bool:
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            return self._load_from_xml_node(root, media_manager)
        except Exception as e:
            log.error(f"An unexpected error occurred while loading model {filename}: {e}")
            return False

    def index_of_pose(self, pose_name: str) -> int:
        for i, pose in enumerate(self.poses):
            if pose.name == pose_name:
                return i
        return -1

class RealTimeAnimationKey:
    def __init__(self, pose: int = 0, time: int = 0):
        self.pose = pose
        self.time = time

class RealTimeAnimation:
    def __init__(self):
        self.keys: List[RealTimeAnimationKey] = []
        self.trigger: int = 50 

class RealTimeModel:
    def __init__(self):
        self._actual_pose: Optional[ModelTreeNode] = None
        self._pose_roots: List[TransfTreeNode] = []
        self._animations: List[RealTimeAnimation] = []

    @property
    def actual(self) -> Optional[ModelTreeNode]:
        return self._actual_pose

    def _clone_tree_with_pose(self, pose: Optional[Pose], node: ModelTreeNode) -> TransfTreeNode:
        new_transf_node = TransfTreeNode()
        if pose is None:
            new_transf_node.transf = node.transf.clone()
        else:
            pose_transf_diff = pose.get_transf_for_node(node.name, False)
            if pose_transf_diff is not None:
                new_transf_node.transf = node.transf.sum(pose_transf_diff)
            else:
                new_transf_node.transf = node.transf.clone()
        for child_node in node.children:
            new_transf_node.children.append(self._clone_tree_with_pose(pose, child_node))
        return new_transf_node

    def _interpolate_tree(self, tree1: TransfTreeNode, tree2: TransfTreeNode, actual_node: ModelTreeNode, value: float):
        actual_node.transf.pos = interpolate_vector3(tree1.transf.pos, tree2.transf.pos, value)
        actual_node.transf.rot = interpolate_vector3(tree1.transf.rot, tree2.transf.rot, value) 
        actual_node.transf.sca = interpolate_vector3(tree1.transf.sca, tree2.transf.sca, value)
        for i in range(len(tree1.children)):
            self._interpolate_tree(tree1.children[i], tree2.children[i], actual_node.children[i], value)

    def _interpolate_pose(self, pose1_idx: int, pose2_idx: int, value: float):
        if self._actual_pose is None:
            return
        self._interpolate_tree(self._pose_roots[pose1_idx], self._pose_roots[pose2_idx], self._actual_pose, value)

    def _make_animation(self, rta: RealTimeAnimation, anim: Animation, model: Model):
        rta.trigger = 50 
        rta.keys = []
        for key in anim.keys:
            if key.trigger:
                rta.trigger = key.time
            rta.keys.append(RealTimeAnimationKey(model.index_of_pose(key.pose_name), key.time))
        rta.keys.sort(key=lambda k: k.time)

    def build(self, model: Model):
        self._pose_roots.clear()
        for pose in model.poses:
            self._pose_roots.append(self._clone_tree_with_pose(pose, model.root))
        self._actual_pose = model.root.clone_deep()
        self._animations.clear()
        for anim in model.animations:
            rta = RealTimeAnimation()
            self._make_animation(rta, anim, model)
            self._animations.append(rta)

    def interpolate(self, animation_idx: int, value: float):
        if animation_idx >= len(self._animations):
            return
        anim = self._animations[animation_idx]
        if len(anim.keys) <= 1:
            return
        val_scaled = int(value * 100)
        p_idx = len(anim.keys) - 1 
        for i in range(1, len(anim.keys)):
            if anim.keys[i].time > val_scaled:
                p_idx = i
                break
        key1 = anim.keys[p_idx - 1]
        key2 = anim.keys[p_idx]
        delta_time = (key2.time - key1.time) / 100.0
        interp_factor = 0.0 if delta_time == 0 else (value - (key1.time / 100.0)) / delta_time
        self._interpolate_pose(key1.pose, key2.pose, interp_factor)

    def trigger_passed(self, animation_idx: int, value: float) -> bool:
        if animation_idx >= len(self._animations):
            return False
        return (self._animations[animation_idx].trigger / 100.0) <= value

    def load_from_file(self, filename: str, media_manager: MediaManager) -> bool:
        model = Model()
        if not model.load_from_file(filename, media_manager):
            return False
        self.build(model)
        return True
