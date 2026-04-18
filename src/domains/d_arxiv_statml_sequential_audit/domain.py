"""D_ARXIV_STATML_SEQUENTIAL_AUDIT domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_SEQUENTIAL_AUDIT"
DOMAIN_NAME = "Arxiv StatML Sequential Audit"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.06116v1",
]

INVARIANTS = [
    "check_risk_limit_valid",
    "check_sample_size_valid",
    "check_test_statistic_nonnegative",
    "check_audit_completion",
    "check_population_size_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_SEQUENTIAL_AUDIT_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_SEQUENTIAL_AUDIT_001"]
