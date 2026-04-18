"""D_ARXIV_OBJECTIVE_LINEAR_ALGEBRA domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_OBJECTIVE_LINEAR_ALGEBRA"
DOMAIN_NAME = "Arxiv Signs in Objective Linear Algebra"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.CT",
    "paper:2603.19437v1",
]

INVARIANTS = [
    "check_sign_consistency",
    "check_exterior_power",
    "check_determinant",
    "check_orientation_independence",
    "check_dimension_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_OBJECTIVE_LINEAR_ALGEBRA_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_OBJECTIVE_LINEAR_ALGEBRA_001"]
