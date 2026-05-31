"""Scene property definitions and serializers for Molder V2 state."""

import json

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import PropertyGroup


class MolderV2SceneProperties(PropertyGroup):
    selected_object_name: StringProperty(name="Objet cible", default="")
    conformity_checked: BoolProperty(default=False)
    conformity_status: EnumProperty(items=[("NONE", "Non vérifié", ""), ("OK", "OK", ""), ("WARNING", "WARNING", ""), ("BLOCKED", "BLOCKED", "")], default="NONE")
    conformity_json: StringProperty(default="{}")
    analysis_done: BoolProperty(default=False)
    analysis_json: StringProperty(default="{}")
    classification_json: StringProperty(default="{}")
    strategy_json: StringProperty(default="{}")
    cut_piece_mode: EnumProperty(
        name="Nombre de guides/pièces",
        items=[("2", "2", "Deux demi-espaces"), ("3", "3", "Trois secteurs de 120 degrés"), ("4", "4", "Quatre secteurs de 90 degrés"), ("CUSTOM", "Personnalisé", "Nombre défini manuellement")],
        default="4",
    )
    cut_piece_count: IntProperty(name="Nombre calculé", default=4, min=2, max=8)
    custom_piece_count: IntProperty(name="Personnalisé", default=4, min=2, max=8)
    relief_threshold: FloatProperty(name="Seuil relief", default=0.12, min=0.01, max=1.0)
    undercut_threshold: FloatProperty(name="Seuil contre-dépouille", default=0.22, min=0.01, max=1.0)
    debug_mode: BoolProperty(name="Mode debug", default=False)
    show_normals: BoolProperty(name="Afficher normales", default=False)
    show_bounding_box: BoolProperty(name="Afficher bounding box", default=True)
    show_detected_axes: BoolProperty(name="Afficher axes détectés", default=True)
    advanced_open: BoolProperty(name="Avancé", default=False)
    strategy_validated: BoolProperty(default=False)
    validation_json: StringProperty(default="{}")


def encode_dataclass(value) -> str:
    data = value.__dict__ if hasattr(value, "__dict__") else value
    return json.dumps(data, ensure_ascii=False, default=str)


def decode_json(value: str, default=None):
    if default is None:
        default = {}
    try:
        return json.loads(value or "{}")
    except json.JSONDecodeError:
        return default


def store_report(scene, report):
    props = scene.molder_v2
    props.conformity_checked = True
    props.conformity_status = report.conformity_status
    props.conformity_json = encode_dataclass(report)


def store_analysis(scene, analysis, classification, strategy):
    props = scene.molder_v2
    props.analysis_done = True
    props.analysis_json = encode_dataclass(analysis)
    props.classification_json = encode_dataclass(classification)
    props.strategy_json = encode_dataclass(strategy)
    props.cut_piece_count = strategy.recommended_piece_count
    props.cut_piece_mode = str(strategy.recommended_piece_count) if strategy.recommended_piece_count in {2, 3, 4} else "CUSTOM"


def reset_runtime_state(scene):
    props = scene.molder_v2
    props.conformity_checked = False
    props.conformity_status = "NONE"
    props.conformity_json = "{}"
    props.analysis_done = False
    props.analysis_json = "{}"
    props.classification_json = "{}"
    props.strategy_json = "{}"
    props.strategy_validated = False
    props.validation_json = "{}"
