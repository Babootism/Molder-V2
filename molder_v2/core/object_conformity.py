"""Object conformity checks executed before any mould strategy analysis."""

from dataclasses import dataclass, field
from math import isfinite

from mathutils import Vector

from ..utils.math_utils import bounds_from_world_corners
from ..utils.mesh_utils import boundary_non_manifold_from_polygons, loose_part_count


@dataclass
class ConformityReport:
    is_mesh: bool = False
    has_faces: bool = False
    dimensions_valid: bool = False
    scale_applied_or_warning: bool = True
    is_manifold: bool = False
    is_closed: bool = False
    has_boundary_edges: bool = False
    has_non_manifold_edges: bool = False
    normals_consistent: bool = True
    has_inverted_normals_warning: bool = False
    has_internal_faces_warning: bool = False
    is_likely_shell: bool = False
    is_likely_solid: bool = False
    has_multiple_loose_parts: bool = False
    conformity_status: str = "BLOCKED"
    reasons: list[str] = field(default_factory=list)
    recommended_action: str = "Sélectionner un mesh exploitable."
    boundary_edge_count: int = 0
    non_manifold_edge_count: int = 0
    loose_part_count: int = 0


def check_object_conformity(obj) -> ConformityReport:
    report = ConformityReport()
    if obj is None:
        report.reasons.append("Aucun objet sélectionné.")
        return report

    report.is_mesh = obj.type == "MESH"
    if not report.is_mesh:
        report.reasons.append("L'objet sélectionné n'est pas un mesh.")
        return report

    mesh = obj.data
    report.has_faces = len(mesh.polygons) > 0
    if not mesh.vertices or not report.has_faces:
        report.reasons.append("Le mesh est vide ou ne contient aucune face.")
        return report

    _, _, dims, _ = bounds_from_world_corners(obj)
    report.dimensions_valid = all(isfinite(value) and value > 1e-6 for value in dims)
    if not report.dimensions_valid:
        report.reasons.append("Les dimensions sont nulles ou incohérentes.")
        return report

    scale_values = tuple(abs(value) for value in obj.scale)
    report.scale_applied_or_warning = all(abs(value - 1.0) < 0.01 for value in scale_values)
    if not report.scale_applied_or_warning:
        report.reasons.append("Échelle non appliquée : l'analyse reste possible mais moins fiable.")

    boundary_edges, non_manifold_edges, _ = boundary_non_manifold_from_polygons(mesh)
    edge_total = max(1, len(mesh.edges))
    non_manifold_ratio = non_manifold_edges / edge_total
    report.boundary_edge_count = boundary_edges
    report.non_manifold_edge_count = non_manifold_edges
    report.has_boundary_edges = boundary_edges > 0
    report.has_non_manifold_edges = non_manifold_edges > 0
    report.is_closed = boundary_edges == 0
    report.is_manifold = non_manifold_edges == 0

    report.normals_consistent = _normals_look_consistent(obj)
    report.has_inverted_normals_warning = not report.normals_consistent

    parts = loose_part_count(mesh)
    report.loose_part_count = parts
    report.has_multiple_loose_parts = parts > 1
    if report.has_multiple_loose_parts:
        report.reasons.append("Plusieurs parties détachées détectées.")

    thin_ratio = min(dims) / max(dims)
    report.is_likely_shell = report.has_boundary_edges and thin_ratio < 0.08
    report.has_internal_faces_warning = _suspect_internal_faces(mesh)
    report.is_likely_solid = report.is_closed and report.is_manifold and not report.has_internal_faces_warning

    _classify_report(report, non_manifold_ratio)
    return report


def _normals_look_consistent(obj) -> bool:
    mesh = obj.data
    center = sum((obj.matrix_world @ vertex.co for vertex in mesh.vertices), Vector((0.0, 0.0, 0.0))) / max(1, len(mesh.vertices))
    suspicious = 0
    for poly in mesh.polygons:
        world_center = obj.matrix_world @ poly.center
        world_normal = obj.matrix_world.to_3x3() @ poly.normal
        if (world_center - center).dot(world_normal) < -1e-6:
            suspicious += 1
    return suspicious / max(1, len(mesh.polygons)) < 0.35


def _suspect_internal_faces(mesh) -> bool:
    if not mesh.polygons:
        return False
    tiny_faces = sum(1 for poly in mesh.polygons if poly.area < 1e-10)
    return tiny_faces / len(mesh.polygons) > 0.05


def _classify_report(report: ConformityReport, non_manifold_ratio: float) -> None:
    if report.has_non_manifold_edges:
        report.reasons.append(f"Arêtes non-manifold détectées : {report.non_manifold_edge_count}.")
    if report.has_boundary_edges:
        report.reasons.append(f"Bords ouverts détectés : {report.boundary_edge_count}.")
    if report.has_inverted_normals_warning:
        report.reasons.append("Normales potentiellement incohérentes.")
    if report.has_internal_faces_warning:
        report.reasons.append("Faces internes ou dégénérées suspectées.")
    if report.is_likely_shell:
        report.reasons.append("Simple surface ou coque sans épaisseur probable.")

    if report.is_likely_shell or non_manifold_ratio > 0.18:
        report.conformity_status = "BLOCKED"
        report.recommended_action = "Créer un volume maître fermé représentant l'enveloppe extérieure avant l'analyse."
        return

    warnings = [
        not report.scale_applied_or_warning,
        report.has_boundary_edges,
        report.has_non_manifold_edges,
        report.has_inverted_normals_warning,
        report.has_internal_faces_warning,
        report.has_multiple_loose_parts,
    ]
    if any(warnings):
        report.conformity_status = "WARNING"
        report.recommended_action = "Analyse autorisée avec prudence ; idéalement utiliser un volume maître propre, fermé et sans faces internes."
        return

    report.conformity_status = "OK"
    report.recommended_action = "Objet exploitable pour une première analyse Molder V2."
