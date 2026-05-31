"""Operator: clear generated Molder V2 objects only."""

import bpy

from ..core.scene_metadata import reset_runtime_state
from ..utils.naming import is_molder_object


class MOLDER_V2_OT_clear_molder_scene(bpy.types.Operator):
    bl_idname = "molder_v2.clear_molder_scene"
    bl_label = "Effacer éléments Molder V2"
    bl_description = "Supprime uniquement les objets générés par Molder V2"

    def execute(self, context):
        removed = 0
        for obj in list(bpy.data.objects):
            if is_molder_object(obj):
                bpy.data.objects.remove(obj, do_unlink=True)
                removed += 1
        reset_runtime_state(context.scene)
        self.report({"INFO"}, f"{removed} élément(s) Molder V2 supprimé(s).")
        return {"FINISHED"}
