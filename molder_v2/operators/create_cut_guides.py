"""Operator: create editable cut guide planes."""

import bpy

from ..core.cut_guides import create_cut_guides


class MOLDER_V2_OT_create_cut_guides(bpy.types.Operator):
    bl_idname = "molder_v2.create_cut_guides"
    bl_label = "Créer guides de découpe"
    bl_description = "Crée des guides radiaux manipulables et non destructifs"

    @classmethod
    def poll(cls, context):
        props = getattr(context.scene, "molder_v2", None)
        return bool(context.object and props and props.analysis_done)

    def execute(self, context):
        obj = context.object
        if obj is None or obj.type != "MESH":
            self.report({"ERROR"}, "Sélectionner le mesh cible avant de créer les guides.")
            return {"CANCELLED"}
        props = context.scene.molder_v2
        count = props.custom_piece_count if props.cut_piece_mode == "CUSTOM" else int(props.cut_piece_mode)
        props.cut_piece_count = count
        guides = create_cut_guides(obj, count)
        self.report({"INFO"}, f"{len(guides)} guides de découpe créés.")
        return {"FINISHED"}
