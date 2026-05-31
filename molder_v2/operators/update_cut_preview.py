"""Operator: update non-destructive cut preview."""

import bpy

from ..core.preview import update_preview


class MOLDER_V2_OT_update_cut_preview(bpy.types.Operator):
    bl_idname = "molder_v2.update_cut_preview"
    bl_label = "Mettre à jour aperçu"
    bl_description = "Met à jour une prévisualisation non destructive des guides"

    def execute(self, context):
        obj = context.object
        if obj is None or obj.type != "MESH":
            self.report({"ERROR"}, "Sélectionner le mesh cible pour mettre à jour l'aperçu.")
            return {"CANCELLED"}
        try:
            update_preview(obj)
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        self.report({"INFO"}, "Aperçu Molder V2 mis à jour.")
        return {"FINISHED"}
