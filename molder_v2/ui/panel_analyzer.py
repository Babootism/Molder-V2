"""Object analyzer panel."""

import bpy

from ..core.scene_metadata import decode_json


class MOLDER_V2_PT_analyzer(bpy.types.Panel):
    bl_label = "Analyse"
    bl_idname = "MOLDER_V2_PT_analyzer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Molder V2"
    bl_parent_id = "MOLDER_V2_PT_main"

    def draw(self, context):
        layout = self.layout
        props = context.scene.molder_v2
        row = layout.row()
        row.enabled = props.conformity_status in {"OK", "WARNING"}
        row.operator("molder_v2.analyze_object", icon="VIEWZOOM")
        if props.conformity_status == "BLOCKED":
            layout.label(text="Analyse bloquée : objet non conforme", icon="ERROR")
        if not props.analysis_done:
            return
        analysis = decode_json(props.analysis_json)
        classification = decode_json(props.classification_json)
        strategy = decode_json(props.strategy_json)
        layout.separator()
        layout.label(text=f"Type probable : {classification.get('object_type', 'UNKNOWN')}")
        layout.label(text=f"Confiance : {classification.get('confidence_score', 0):.2f}")
        layout.label(text=f"Dimensions : H {analysis.get('height', 0):.3f} / W {analysis.get('width', 0):.3f} / D {analysis.get('depth', 0):.3f}")
        layout.label(text=f"Axe principal : {analysis.get('principal_axis', 'Z')}")
        layout.label(text=f"Ouverture supérieure : {_probable(analysis.get('has_top_opening'))}")
        layout.label(text=f"Creux probable : {_probable(analysis.get('is_probably_hollow'))}")
        layout.label(text=f"Fond probable : {_probable(analysis.get('has_probable_bottom'))}")
        layout.label(text=f"Anse/excroissance : {_probable(analysis.get('has_lateral_protrusion'))}")
        layout.label(text=f"Relief extérieur : {analysis.get('relief_external_level', 'NONE')}")
        layout.label(text=f"Relief intérieur : {analysis.get('relief_internal_level', 'NONE')}")
        layout.label(text=f"Contre-dépouille : {analysis.get('undercut_level', 'NONE')}")
        layout.label(text=f"Pièces recommandées : {strategy.get('recommended_piece_count', 4)}")
        layout.label(text=f"Stratégie : {strategy.get('strategy_name', '')}")
        if classification.get("reasons"):
            box = layout.box()
            box.label(text="Raisons")
            for reason in classification.get("reasons", [])[:5]:
                box.label(text=f"• {reason}")
        warnings = classification.get("warnings", []) + strategy.get("warnings", [])
        if warnings:
            box = layout.box()
            box.label(text="Avertissements", icon="ERROR")
            for warning in warnings[:5]:
                box.label(text=f"• {warning}")


def _probable(value):
    return "oui" if value else "non"
