"""Creation of non-destructive editable cut guide planes."""

from math import radians

import bpy
from mathutils import Vector

from ..utils.math_utils import bounds_from_world_corners
from ..utils.naming import GUIDES_COLLECTION, ROOT_COLLECTION, guide_name


def ensure_molder_collections():
    root = _ensure_collection(ROOT_COLLECTION, bpy.context.scene.collection)
    guides = _ensure_collection(GUIDES_COLLECTION, root)
    _ensure_collection("MOLDER_V2_PREVIEW", root)
    _ensure_collection("MOLDER_V2_DEBUG", root)
    return root, guides


def create_cut_guides(target_obj, piece_count: int):
    _, guides_collection = ensure_molder_collections()
    clear_guides()
    _, _, dims, center = bounds_from_world_corners(target_obj)
    size = max(dims.x, dims.y, dims.z) * 1.35
    height = max(dims.z, size * 0.25) * 1.2
    material = _guide_material()
    guides = []
    for index in range(1, piece_count + 1):
        angle = (360.0 / piece_count) * (index - 1)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
        guide = bpy.context.object
        guide.name = guide_name(index)
        guide.data.name = f"{guide.name}_MESH"
        guide.dimensions = (0.012 * size, size, height)
        guide.rotation_euler[2] = radians(angle)
        guide.display_type = "TEXTURED"
        guide.show_transparent = True
        guide["molder_v2_generated"] = True
        guide["molder_v2_type"] = "CUT_GUIDE"
        guide["molder_v2_index"] = index
        guide["molder_v2_angle"] = angle
        guide["molder_v2_target_object_name"] = target_obj.name
        guide["molder_v2_validated"] = False
        guide.data.materials.append(material)
        _move_to_collection(guide, guides_collection)
        guides.append(guide)
    return guides


def list_cut_guides():
    return [obj for obj in bpy.data.objects if obj.get("molder_v2_type") == "CUT_GUIDE"]


def clear_guides():
    for obj in list_cut_guides():
        bpy.data.objects.remove(obj, do_unlink=True)


def mark_guides_validated():
    for guide in list_cut_guides():
        guide["molder_v2_validated"] = True


def _ensure_collection(name, parent):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    if collection.name not in [child.name for child in parent.children]:
        parent.children.link(collection)
    return collection


def _move_to_collection(obj, collection):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def _guide_material():
    material = bpy.data.materials.get("MOLDER_V2_GUIDE_MATERIAL")
    if material is None:
        material = bpy.data.materials.new("MOLDER_V2_GUIDE_MATERIAL")
    material.diffuse_color = (0.1, 0.55, 1.0, 0.28)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Alpha"].default_value = 0.28
    material.blend_method = "BLEND"
    material.show_transparent_back = True
    return material
