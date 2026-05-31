"""Rule-based object classification for Molder V2 Phase 1."""

from dataclasses import dataclass, field


@dataclass
class ClassificationResult:
    object_type: str = "UNKNOWN"
    confidence_score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def classify_object(analysis) -> ClassificationResult:
    result = ClassificationResult(warnings=list(analysis.warnings))
    max_plan = max(analysis.width, analysis.depth)
    flat_ratio = analysis.height / max(max_plan, 1e-9)

    if flat_ratio < 0.22:
        result.object_type = "PLATE"
        result.confidence_score = 0.82
        result.reasons.append("Hauteur très faible par rapport à la largeur/profondeur.")
        return result

    if analysis.has_top_opening and analysis.has_lateral_protrusion:
        result.object_type = "MUG_WITH_HANDLE"
        result.confidence_score = min(0.88, 0.55 + analysis.lateral_asymmetry)
        result.reasons.append("Ouverture supérieure probable et excroissance latérale significative.")
        result.warnings.append("L'anse nécessitera probablement une pièce dédiée dans une phase future.")
        return result

    if analysis.has_top_opening and analysis.top_radius > analysis.bottom_radius * 1.18 and flat_ratio < 1.25:
        result.object_type = "BOWL"
        result.confidence_score = 0.76
        result.reasons.append("Ouverture supérieure probable avec rayon haut supérieur au rayon bas.")
        return result

    if analysis.has_top_opening and flat_ratio >= 0.75 and not analysis.has_lateral_protrusion:
        result.object_type = "SIMPLE_CUP_GLASS"
        result.confidence_score = 0.72 + min(0.18, analysis.top_opening_score * 0.18)
        result.reasons.append("Forme verticale avec ouverture supérieure probable et sans anse détectée.")
        return result

    if analysis.lateral_asymmetry > 0.28 or analysis.relief_external_level in {"MEDIUM", "HIGH"}:
        result.object_type = "FREEFORM_OBJECT"
        result.confidence_score = 0.64
        result.reasons.append("Asymétrie ou relief important ne correspondant pas aux familles simples.")
        return result

    result.object_type = "UNKNOWN"
    result.confidence_score = 0.38
    result.reasons.append("Les indicateurs V1 ne permettent pas une classification fiable.")
    result.warnings.append("Créer uniquement des guides manuels si nécessaire.")
    return result
