"""Simplified undercut detection for Phase 1 diagnostics."""

from ..utils.math_utils import risk_from_score


def detect_undercut_level(obj, axis="Z") -> tuple[str, float]:
    mesh = obj.data
    if not mesh.polygons:
        return "NONE", 0.0
    risky = 0
    for poly in mesh.polygons:
        normal = obj.matrix_world.to_3x3() @ poly.normal
        radial_score = abs(normal.z) if axis == "Z" else 0.0
        if normal.z < -0.18 or radial_score < 0.08:
            risky += 1
    score = risky / max(1, len(mesh.polygons))
    return risk_from_score(score), score
