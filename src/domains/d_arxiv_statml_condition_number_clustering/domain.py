"""D_ARXIV_STATML_CONDITION_NUMBER_CLUSTERING domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_CONDITION_NUMBER_CLUSTERING"
DOMAIN_NAME = "Arxiv StatML Condition Number Clustering"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.07744v1",
]

INVARIANTS = [
    "check_condition_number_valid",
    "check_cluster_count_valid",
    "check_separation_margin_positive",
    "check_stability",
    "check_intra_variance_nonnegative",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_CONDITION_NUMBER_CLUSTERING_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_CONDITION_NUMBER_CLUSTERING_001"]
