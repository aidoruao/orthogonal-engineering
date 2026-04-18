"""D_ARXIV_STATML_GAUSSIAN_APPROXIMATION domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_GAUSSIAN_APPROXIMATION"
DOMAIN_NAME = "Arxiv StatML Gaussian Approximation"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.07323v1",
]

INVARIANTS = [
    "check_asymptotic_normality",
    "check_sample_count_positive",
    "check_approximation_error_valid",
    "check_convergence_rate_positive",
    "check_dimension_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_GAUSSIAN_APPROXIMATION_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_GAUSSIAN_APPROXIMATION_001"]
