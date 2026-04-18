"""D_ARXIV_STATML_SPARSE_SVM domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_SPARSE_SVM"
DOMAIN_NAME = "Arxiv StatML Sparse SVM"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.07748v1",
]

INVARIANTS = [
    "check_sparsity_ratio_valid",
    "check_epsilon_nonnegative",
    "check_support_vector_count_positive",
    "check_generalization_bound_valid",
    "check_sparsity_consistency",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_SPARSE_SVM_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_SPARSE_SVM_001"]
