"""Math helpers for Blender geometry diagnostics."""

from mathutils import Vector


def safe_divide(value: float, divisor: float, default: float = 0.0) -> float:
    if abs(divisor) < 1e-9:
        return default
    return value / divisor


def bounds_from_world_corners(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
    maxs = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
    dims = maxs - mins
    center = (mins + maxs) * 0.5
    return mins, maxs, dims, center


def risk_from_score(score: float) -> str:
    if score < 0.08:
        return "NONE"
    if score < 0.22:
        return "LOW"
    if score < 0.45:
        return "MEDIUM"
    return "HIGH"
