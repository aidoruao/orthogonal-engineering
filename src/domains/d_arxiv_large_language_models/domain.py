"""D_ARXIV_LARGE_LANGUAGE_MODELS domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_LARGE_LANGUAGE_MODELS"
DOMAIN_NAME = "Arxiv Large Language Models"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09544v1",
]

INVARIANTS = [
    "check_harm_weight_compactness",
    "check_harm_benign_mechanism_separation",
    "check_targeted_pruning_selectivity",
    "check_cross_harm_generalization",
    "check_alignment_feature_localization",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_LARGE_LANGUAGE_MODELS_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_LARGE_LANGUAGE_MODELS_001"]
