"""Operator: check selected object conformity."""

import bpy

from ..core.object_conformity import check_object_conformity
from ..core.scene_metadata import reset_runtime_state, store_report


class MOLDER_V2_OT_check_conformity(bpy.types.Operator):
    bl_idname = "molder_v2.check_conformity"
    bl_label = "Vérifier conformité"
    bl_description = "Vérifie si l'objet sélectionné est exploitable pour Molder V2"

    def execute(self, context):
        obj = context.object
        reset_runtime_state(context.scene)
        report = check_object_conformity(obj)
        if obj:
            context.scene.molder_v2.selected_object_name = obj.name
        store_report(context.scene, report)
        icon = "ERROR" if report.conformity_status == "BLOCKED" else "WARNING" if report.conformity_status == "WARNING" else "INFO"
        self.report({icon}, f"Conformité Molder V2 : {report.conformity_status}")
        return {"FINISHED"}
