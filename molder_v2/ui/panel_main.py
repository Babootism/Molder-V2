"""Main Molder V2 sidebar panel."""

import bpy


class MOLDER_V2_PT_main(bpy.types.Panel):
    bl_label = "Molder V2"
    bl_idname = "MOLDER_V2_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Molder V2"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        props = context.scene.molder_v2
        box = layout.box()
        box.label(text="Objet", icon="OBJECT_DATA")
        box.label(text=f"Sélection : {obj.name if obj else 'Aucun'}")
        box.operator("molder_v2.check_conformity", icon="CHECKMARK")
        box.operator("molder_v2.clear_molder_scene", icon="TRASH")
        if props.strategy_validated:
            layout.label(text="Stratégie validée", icon="LOCKED")
