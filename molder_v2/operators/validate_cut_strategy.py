"""Operator: validate current guide transforms for future mold generation."""

import json
from datetime import datetime, timezone

import bpy

from ..core.cut_guides import list_cut_guides, mark_guides_validated
from ..core.scene_metadata import decode_json
from ..utils.naming import ROOT_COLLECTION, VALIDATED_COLLECTION


class MOLDER_V2_OT_validate_cut_strategy(bpy.types.Operator):
    bl_idname = "molder_v2.validate_cut_strategy"
    bl_label = "Valider stratégie"
    bl_description = "Enregistre la position actuelle des guides pour les futures phases"

    def execute(self, context):
        guides = list_cut_guides()
        if not guides:
            self.report({"ERROR"}, "Les guides doivent être créés avant validation.")
            return {"CANCELLED"}
        props = context.scene.molder_v2
        classification = decode_json(props.classification_json)
        strategy = decode_json(props.strategy_json)
        analysis = decode_json(props.analysis_json)
        conformity = decode_json(props.conformity_json)
        payload = {
            "target_object_name": props.selected_object_name or (context.object.name if context.object else ""),
            "object_type": classification.get("object_type", "UNKNOWN"),
            "conformity_status": conformity.get("conformity_status", props.conformity_status),
            "piece_count": len(guides),
            "guides": [_guide_payload(guide) for guide in guides],
            "undercut_level": analysis.get("undercut_level", "UNKNOWN"),
            "strategy_recommended": strategy.get("strategy_name", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "validated": True,
        }
        mark_guides_validated()
        _ensure_validated_marker(payload)
        props.strategy_validated = True
        props.validation_json = json.dumps(payload, ensure_ascii=False)
        self.report({"INFO"}, "Stratégie de découpe validée.")
        return {"FINISHED"}


def _guide_payload(guide):
    return {
        "name": guide.name,
        "index": guide.get("molder_v2_index"),
        "angle": guide.get("molder_v2_angle"),
        "matrix_world": [list(row) for row in guide.matrix_world],
        "location": list(guide.location),
        "rotation_euler": list(guide.rotation_euler),
    }


def _ensure_validated_marker(payload):
    root = bpy.data.collections.get(ROOT_COLLECTION) or bpy.data.collections.new(ROOT_COLLECTION)
    if root.name not in [child.name for child in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(root)
    collection = bpy.data.collections.get(VALIDATED_COLLECTION) or bpy.data.collections.new(VALIDATED_COLLECTION)
    if collection.name not in [child.name for child in root.children]:
        root.children.link(collection)
    bpy.ops.object.empty_add(type="CUBE", location=(0, 0, 0))
    marker = bpy.context.object
    marker.name = "MOLDER_V2_VALIDATED_STRATEGY"
    marker["molder_v2_generated"] = True
    marker["molder_v2_type"] = "VALIDATED_STRATEGY"
    marker["molder_v2_validation_json"] = json.dumps(payload, ensure_ascii=False)
    for current in list(marker.users_collection):
        current.objects.unlink(marker)
    collection.objects.link(marker)
