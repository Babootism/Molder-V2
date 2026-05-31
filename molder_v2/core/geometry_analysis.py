"""Geometry analysis for understanding the selected master object."""

from dataclasses import dataclass, field
from statistics import mean, pstdev

from ..utils.math_utils import bounds_from_world_corners, safe_divide
from ..utils.mesh_utils import vertex_world_positions
from .undercut_detection import detect_undercut_level


@dataclass
class GeometryAnalysis:
    width: float = 0.0
    depth: float = 0.0
    height: float = 0.0
    ratio_height_width: float = 0.0
    ratio_height_depth: float = 0.0
    center: tuple[float, float, float] = (0.0, 0.0, 0.0)
    principal_axis: str = "Z"
    volume_approx: float = 0.0
    surface_area: float = 0.0
    orientation_warning: str = ""
    top_opening_score: float = 0.0
    has_top_opening: bool = False
    bottom_score: float = 0.0
    has_probable_bottom: bool = False
    lateral_asymmetry: float = 0.0
    has_lateral_protrusion: bool = False
    radius_profile: list[tuple[float, float]] = field(default_factory=list)
    top_radius: float = 0.0
    bottom_radius: float = 0.0
    relief_external_level: str = "NONE"
    relief_internal_level: str = "NONE"
    undercut_level: str = "NONE"
    undercut_score: float = 0.0
    is_probably_hollow: bool = False
    warnings: list[str] = field(default_factory=list)


def analyze_geometry(obj, relief_threshold: float = 0.12) -> GeometryAnalysis:
    mins, maxs, dims, center = bounds_from_world_corners(obj)
    analysis = GeometryAnalysis(
        width=dims.x,
        depth=dims.y,
        height=dims.z,
        ratio_height_width=safe_divide(dims.z, dims.x),
        ratio_height_depth=safe_divide(dims.z, dims.y),
        center=(center.x, center.y, center.z),
        volume_approx=dims.x * dims.y * dims.z,
        surface_area=sum(poly.area for poly in obj.data.polygons),
    )
    analysis.principal_axis, analysis.orientation_warning = _detect_axis(dims)
    if analysis.orientation_warning:
        analysis.warnings.append(analysis.orientation_warning)

    vertices = vertex_world_positions(obj)
    analysis.radius_profile = _radius_profile(vertices, mins.z, maxs.z, center)
    if analysis.radius_profile:
        analysis.bottom_radius = analysis.radius_profile[0][1]
        analysis.top_radius = analysis.radius_profile[-1][1]

    analysis.top_opening_score, analysis.has_top_opening = _estimate_top_opening(vertices, mins.z, maxs.z, center)
    analysis.bottom_score, analysis.has_probable_bottom = _estimate_bottom(obj, mins.z, maxs.z, center)
    analysis.lateral_asymmetry, analysis.has_lateral_protrusion = _detect_lateral_protrusion(vertices, center)
    analysis.relief_external_level = _detect_relief_level(analysis.radius_profile, relief_threshold)
    analysis.relief_internal_level = "LOW" if analysis.top_opening_score > 0.55 and analysis.has_probable_bottom else "NONE"
    analysis.undercut_level, analysis.undercut_score = detect_undercut_level(obj, analysis.principal_axis)
    analysis.is_probably_hollow = analysis.has_top_opening and analysis.has_probable_bottom and analysis.relief_internal_level != "NONE"
    if not analysis.has_probable_bottom:
        analysis.warnings.append("Fond probable non détecté ou fond potentiellement ouvert.")
    return analysis


def _detect_axis(dims):
    values = {"X": dims.x, "Y": dims.y, "Z": dims.z}
    axis = max(values, key=values.get)
    if axis != "Z" and values[axis] > values["Z"] * 1.35:
        return "Z", "Objet possiblement orienté hors axe vertical ; l'axe Z est conservé pour la V1."
    return "Z", ""


def _radius_profile(vertices, z_min, z_max, center, slices=8):
    height = max(1e-9, z_max - z_min)
    buckets = [[] for _ in range(slices)]
    for vertex in vertices:
        index = min(slices - 1, max(0, int(((vertex.z - z_min) / height) * slices)))
        radius = ((vertex.x - center.x) ** 2 + (vertex.y - center.y) ** 2) ** 0.5
        buckets[index].append(radius)
    profile = []
    for index, radii in enumerate(buckets):
        z_ratio = (index + 0.5) / slices
        profile.append((z_ratio, mean(radii) if radii else 0.0))
    return profile


def _estimate_top_opening(vertices, z_min, z_max, center):
    height = max(1e-9, z_max - z_min)
    top_vertices = [v for v in vertices if v.z > z_max - height * 0.12]
    if len(top_vertices) < 4:
        return 0.0, False
    radii = [((v.x - center.x) ** 2 + (v.y - center.y) ** 2) ** 0.5 for v in top_vertices]
    avg_radius = mean(radii) if radii else 0.0
    center_gap = min(radii) / max(avg_radius, 1e-9)
    ring_strength = min(1.0, len(top_vertices) / max(8, len(vertices) * 0.08))
    score = max(0.0, min(1.0, center_gap * 0.65 + ring_strength * 0.35))
    return score, score > 0.45


def _estimate_bottom(obj, z_min, z_max, center):
    height = max(1e-9, z_max - z_min)
    bottom_polys = [poly for poly in obj.data.polygons if (obj.matrix_world @ poly.center).z < z_min + height * 0.14]
    if not bottom_polys:
        return 0.0, False
    downward = sum(1 for poly in bottom_polys if (obj.matrix_world.to_3x3() @ poly.normal).z < -0.35)
    score = downward / max(1, len(bottom_polys))
    return score, score > 0.25 or len(bottom_polys) > 2


def _detect_lateral_protrusion(vertices, center):
    if not vertices:
        return 0.0, False
    xs = [v.x - center.x for v in vertices]
    ys = [v.y - center.y for v in vertices]
    x_asym = abs(max(xs) + min(xs)) / max(1e-9, max(xs) - min(xs))
    y_asym = abs(max(ys) + min(ys)) / max(1e-9, max(ys) - min(ys))
    score = max(x_asym, y_asym)
    return score, score > 0.22


def _detect_relief_level(profile, threshold):
    radii = [radius for _, radius in profile if radius > 0]
    if len(radii) < 3:
        return "NONE"
    variation = pstdev(radii) / max(mean(radii), 1e-9)
    if variation < threshold:
        return "NONE"
    if variation < threshold * 1.7:
        return "LOW"
    if variation < threshold * 2.6:
        return "MEDIUM"
    return "HIGH"
