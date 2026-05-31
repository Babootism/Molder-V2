"""Simple non-destructive visual preview objects."""

import bpy
from mathutils import Vector

from ..utils.math_utils import bounds_from_world_corners
from ..utils.naming import PREVIEW_COLLECTION, PREVIEW_PREFIX, ROOT_COLLECTION
from .cut_guides import list_cut_guides


def update_preview(target_obj):
    guides = list_cut_guides()
    if not guides:
        raise ValueError("Les guides doivent être créés avant la prévisualisation.")
    clear_preview()
    collection = _ensure_preview_collection()
    _, _, dims, center = bounds_from_world_corners(target_obj)
    _create_bbox(center, dims, collection)
    _create_axis(center, dims, collection)
    return True


def clear_preview():
    for obj in list(bpy.data.objects):
        if obj.get("molder_v2_type") == "PREVIEW":
            bpy.data.objects.remove(obj, do_unlink=True)


def _ensure_preview_collection():
    root = bpy.data.collections.get(ROOT_COLLECTION) or bpy.data.collections.new(ROOT_COLLECTION)
    if root.name not in [child.name for child in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(root)
    collection = bpy.data.collections.get(PREVIEW_COLLECTION) or bpy.data.collections.new(PREVIEW_COLLECTION)
    if collection.name not in [child.name for child in root.children]:
        root.children.link(collection)
    return collection


def _create_bbox(center, dims, collection):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = f"{PREVIEW_PREFIX}_BOUNDING_BOX"
    obj.display_type = "WIRE"
    obj.dimensions = (dims.x, dims.y, dims.z)
    obj["molder_v2_generated"] = True
    obj["molder_v2_type"] = "PREVIEW"
    _move_to_collection(obj, collection)


def _create_axis(center, dims, collection):
    bpy.ops.object.empty_add(type="SINGLE_ARROW", location=Vector((center.x, center.y, center.z + dims.z * 0.55)))
    obj = bpy.context.object
    obj.name = f"{PREVIEW_PREFIX}_AXIS_Z"
    obj.scale = (max(dims) * 0.25, max(dims) * 0.25, max(dims) * 0.25)
    obj["molder_v2_generated"] = True
    obj["molder_v2_type"] = "PREVIEW"
    _move_to_collection(obj, collection)


def _move_to_collection(obj, collection):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
