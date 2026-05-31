"""Operator: analyze selected object geometry and propose a strategy."""

import bpy

from ..core.cut_strategy import propose_cut_strategy
from ..core.geometry_analysis import analyze_geometry
from ..core.object_classifier import classify_object
from ..core.scene_metadata import store_analysis


class MOLDER_V2_OT_analyze_object(bpy.types.Operator):
    bl_idname = "molder_v2.analyze_object"
    bl_label = "Analyser l'objet"
    bl_description = "Analyse la géométrie et propose une stratégie de séparation"

    @classmethod
    def poll(cls, context):
        props = getattr(context.scene, "molder_v2", None)
        return bool(context.object and props and props.conformity_status in {"OK", "WARNING"})

    def execute(self, context):
        obj = context.object
        if obj is None or obj.type != "MESH":
            self.report({"ERROR"}, "Aucun mesh sélectionné.")
            return {"CANCELLED"}
        props = context.scene.molder_v2
        if props.conformity_status == "BLOCKED":
            self.report({"ERROR"}, "L'objet est non conforme : analyse bloquée.")
            return {"CANCELLED"}
        analysis = analyze_geometry(obj, props.relief_threshold)
        classification = classify_object(analysis)
        strategy = propose_cut_strategy(classification, analysis)
        store_analysis(context.scene, analysis, classification, strategy)
        self.report({"INFO"}, f"Analyse terminée : {classification.object_type}")
        return {"FINISHED"}
