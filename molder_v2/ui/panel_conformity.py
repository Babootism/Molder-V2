"""Conformity report panel."""

import bpy

from ..core.scene_metadata import decode_json


class MOLDER_V2_PT_conformity(bpy.types.Panel):
    bl_label = "Conformité"
    bl_idname = "MOLDER_V2_PT_conformity"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Molder V2"
    bl_parent_id = "MOLDER_V2_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.molder_v2
        if not props.conformity_checked:
            layout.label(text="Non vérifiée")
            return
        data = decode_json(props.conformity_json)
        icon = "CHECKMARK" if props.conformity_status == "OK" else "ERROR" if props.conformity_status == "BLOCKED" else "ERROR"
        layout.label(text=f"Statut : {props.conformity_status}", icon=icon)
        for label, key in [
            ("Mesh valide", "is_mesh"),
            ("Faces présentes", "has_faces"),
            ("Dimensions valides", "dimensions_valid"),
            ("Échelle appliquée", "scale_applied_or_warning"),
            ("Mesh fermé", "is_closed"),
            ("Mesh manifold", "is_manifold"),
            ("Boundary edges", "has_boundary_edges"),
            ("Non-manifold edges", "has_non_manifold_edges"),
            ("Normales cohérentes", "normals_consistent"),
            ("Faces internes suspectées", "has_internal_faces_warning"),
            ("Coque creuse suspectée", "is_likely_shell"),
            ("Volume solide probable", "is_likely_solid"),
            ("Parties détachées", "has_multiple_loose_parts"),
        ]:
            layout.label(text=f"{label} : {_yes_no(data.get(key))}")
        if data.get("reasons"):
            box = layout.box()
            box.label(text="Problèmes détectés")
            for reason in data.get("reasons", [])[:6]:
                box.label(text=f"• {reason}")
        layout.label(text=f"Action : {data.get('recommended_action', '')}")


def _yes_no(value):
    return "oui" if value else "non"
