from OpenGL.GL import *
from core.model import ModelTreeNode, GraphicElementType, RealTimeModel

def apply_transformation(transf):
    """Applies Translation, Rotation, and Scale to the current GL matrix."""
    glTranslatef(transf.pos.x, transf.pos.y, transf.pos.z)
    # Pascal uses degrees for glRotate
    glRotatef(transf.rot.x, 1, 0, 0)
    glRotatef(transf.rot.y, 0, 1, 0)
    glRotatef(transf.rot.z, 0, 0, 1)
    glScalef(transf.sca.x, transf.sca.y, transf.sca.z)

def toggle_face_mode():
    """Toggles culling direction for mirrored scales (negative scale)."""
    mode = glGetIntegerv(GL_FRONT_FACE)
    if mode == GL_CCW:
        glFrontFace(GL_CW)
    else:
        glFrontFace(GL_CCW)

def draw_node_graphics(node: ModelTreeNode):
    """Binds textures and draws the mesh attached to a node."""
    if node.texture is None:
        glDisable(GL_TEXTURE_2D)
    else:
        glEnable(GL_TEXTURE_2D)
        node.texture.bind()

    # Set the material color (RGB 0.0 - 1.0)
    glColor3fv(node.color)

    if node.graphic_element.type == GraphicElementType.MESH:
        if node.graphic_element.mesh:
            node.graphic_element.mesh.draw()

def render_tree_node(node: ModelTreeNode):
    """Recursively walks the model tree and renders each node."""
    glPushMatrix()
    apply_transformation(node.transf)
    
    # Check if we need to flip face culling due to negative scaling
    toggle = node.transf.must_toggle_faces()
    if toggle: toggle_face_mode()
    
    draw_node_graphics(node)
    
    for child in node.children:
        render_tree_node(child)
        
    if toggle: toggle_face_mode()
    glPopMatrix()

def draw_realtime_model(model: RealTimeModel):
    if model and model.actual:
        render_tree_node(model.actual)