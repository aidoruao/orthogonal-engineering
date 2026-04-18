"""D_ARXIV_STATML_MACHINE_UNLEARNING domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_MACHINE_UNLEARNING"
DOMAIN_NAME = "Arxiv StatML Machine Unlearning"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.05669v1",
]

INVARIANTS = [
    "check_minimax_optimality",
    "check_unlearning_error_valid",
    "check_forget_set_valid",
    "check_computational_efficiency",
    "check_dataset_size_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_MACHINE_UNLEARNING_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_MACHINE_UNLEARNING_001"]
