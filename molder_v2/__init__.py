"""Molder V2 Blender add-on entry point."""

bl_info = {
    "name": "Molder V2",
    "author": "OpenAI",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Molder V2",
    "description": "Object conformity, geometry analysis and editable cut guides for ceramic mold planning.",
    "category": "Object",
}

import bpy

from .core.scene_metadata import MolderV2SceneProperties
from .operators.analyze_object import MOLDER_V2_OT_analyze_object
from .operators.check_conformity import MOLDER_V2_OT_check_conformity
from .operators.clear_molder_scene import MOLDER_V2_OT_clear_molder_scene
from .operators.create_cut_guides import MOLDER_V2_OT_create_cut_guides
from .operators.update_cut_preview import MOLDER_V2_OT_update_cut_preview
from .operators.validate_cut_strategy import MOLDER_V2_OT_validate_cut_strategy
from .preferences import MolderV2Preferences
from .ui.panel_analyzer import MOLDER_V2_PT_analyzer
from .ui.panel_conformity import MOLDER_V2_PT_conformity
from .ui.panel_cut_guides import MOLDER_V2_PT_advanced, MOLDER_V2_PT_cut_guides
from .ui.panel_main import MOLDER_V2_PT_main

classes = (
    MolderV2Preferences,
    MolderV2SceneProperties,
    MOLDER_V2_OT_check_conformity,
    MOLDER_V2_OT_analyze_object,
    MOLDER_V2_OT_create_cut_guides,
    MOLDER_V2_OT_update_cut_preview,
    MOLDER_V2_OT_validate_cut_strategy,
    MOLDER_V2_OT_clear_molder_scene,
    MOLDER_V2_PT_main,
    MOLDER_V2_PT_conformity,
    MOLDER_V2_PT_analyzer,
    MOLDER_V2_PT_cut_guides,
    MOLDER_V2_PT_advanced,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.molder_v2 = bpy.props.PointerProperty(type=MolderV2SceneProperties)


def unregister():
    if hasattr(bpy.types.Scene, "molder_v2"):
        del bpy.types.Scene.molder_v2
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
