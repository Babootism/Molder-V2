"""Cut guides and advanced options panels."""

import bpy


class MOLDER_V2_PT_cut_guides(bpy.types.Panel):
    bl_label = "Guides de découpe"
    bl_idname = "MOLDER_V2_PT_cut_guides"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Molder V2"
    bl_parent_id = "MOLDER_V2_PT_main"

    def draw(self, context):
        layout = self.layout
        props = context.scene.molder_v2
        layout.prop(props, "cut_piece_mode", text="Guides / pièces")
        if props.cut_piece_mode == "CUSTOM":
            layout.prop(props, "custom_piece_count", text="Nombre personnalisé")
        col = layout.column()
        col.enabled = props.analysis_done
        col.operator("molder_v2.create_cut_guides", icon="MESH_PLANE")
        col.operator("molder_v2.update_cut_preview", icon="HIDE_OFF")
        col.operator("molder_v2.validate_cut_strategy", icon="FILE_TICK")


class MOLDER_V2_PT_advanced(bpy.types.Panel):
    bl_label = "Avancé"
    bl_idname = "MOLDER_V2_PT_advanced"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Molder V2"
    bl_parent_id = "MOLDER_V2_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.molder_v2
        layout.prop(props, "relief_threshold")
        layout.prop(props, "undercut_threshold")
        layout.prop(props, "debug_mode")
        layout.prop(props, "show_normals")
        layout.prop(props, "show_bounding_box")
        layout.prop(props, "show_detected_axes")
