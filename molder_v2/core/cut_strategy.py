"""Cut strategy recommendations for editable guide generation."""

from dataclasses import dataclass, field


@dataclass
class CutStrategy:
    recommended_piece_count: int = 4
    strategy_name: str = "Guides radiaux verticaux"
    description: str = "Guides radiaux verticaux autour de l'axe Z."
    warnings: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    allow_auto_guides: bool = True


def propose_cut_strategy(classification, analysis) -> CutStrategy:
    object_type = classification.object_type
    strategy = CutStrategy()
    complex_relief = analysis.relief_external_level in {"MEDIUM", "HIGH"}
    risky_undercut = analysis.undercut_level in {"MEDIUM", "HIGH"}

    if object_type == "SIMPLE_CUP_GLASS":
        strategy.recommended_piece_count = 4 if complex_relief or risky_undercut else 2
        strategy.reasons.append("Verre/tasse simple : séparation radiale verticale adaptée en première approximation.")
    elif object_type == "BOWL":
        strategy.recommended_piece_count = 4 if complex_relief or analysis.height > max(analysis.width, analysis.depth) * 0.55 else 2
        strategy.reasons.append("Bol : nombre de pièces ajusté selon profondeur et relief.")
    elif object_type == "PLATE":
        strategy.recommended_piece_count = 2
        strategy.warnings.append("Assiette : stratégie spécifique à développer dans une phase future.")
    elif object_type == "MUG_WITH_HANDLE":
        strategy.recommended_piece_count = 4
        strategy.strategy_name = "Approximation radiale + future pièce d'anse"
        strategy.warnings.append("L'anse nécessitera probablement une pièce dédiée ; guides V1 indicatifs seulement.")
    elif object_type == "FREEFORM_OBJECT":
        strategy.recommended_piece_count = 4
        strategy.strategy_name = "Guides personnalisés à valider manuellement"
        strategy.warnings.append("Validation manuelle indispensable pour une forme libre.")
    else:
        strategy.recommended_piece_count = 4
        strategy.allow_auto_guides = False
        strategy.strategy_name = "Guides manuels uniquement"
        strategy.warnings.append("Classification incertaine : aucune génération automatique recommandée.")

    if classification.confidence_score < 0.55:
        strategy.warnings.append("Confiance faible : vérifier et ajuster les guides avant validation.")
    return strategy
