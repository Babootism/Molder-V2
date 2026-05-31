"""Addon preferences for Molder V2."""

import bpy
from bpy.props import BoolProperty


class MolderV2Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__ or "molder_v2"

    enable_experimental_diagnostics: BoolProperty(
        name="Diagnostics expérimentaux",
        default=False,
        description="Active les diagnostics expérimentaux prévus pour les futures phases",
    )

    def draw(self, context):
        self.layout.prop(self, "enable_experimental_diagnostics")
