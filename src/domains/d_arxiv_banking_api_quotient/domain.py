"""D_ARXIV_BANKING_API_QUOTIENT domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_BANKING_API_QUOTIENT"
DOMAIN_NAME = "Arxiv Universal Quotient of Banking APIs"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.CT",
    "paper:2604.08833v1",
]

INVARIANTS = [
    "check_quotient_existence",
    "check_universality",
    "check_financial_invariants_preserved",
    "check_api_count_positive",
    "check_morphism_count_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_BANKING_API_QUOTIENT_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_BANKING_API_QUOTIENT_001"]
