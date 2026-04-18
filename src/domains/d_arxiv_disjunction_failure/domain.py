"""D_ARXIV_DISJUNCTION_FAILURE domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_DISJUNCTION_FAILURE"
DOMAIN_NAME = "Arxiv Failure of Strong Feasible Disjunction Property"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.LO",
    "paper:2604.04830v1",
]

INVARIANTS = [
    "check_theory_consistency",
    "check_counterexample_witness",
    "check_disjunction_property_failure",
    "check_disjunct_count_positive",
    "check_provability_witness",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_DISJUNCTION_FAILURE_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_DISJUNCTION_FAILURE_001"]
