"""D_ARXIV_PARACONSISTENT_SETS domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_PARACONSISTENT_SETS"
DOMAIN_NAME = "Arxiv Paraconsistent Set Theory Cardinality"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.LO",
    "paper:2604.07094v1",
]

INVARIANTS = [
    "check_paraconsistent_logic",
    "check_cardinality_definition",
    "check_classical_extension",
    "check_set_size_nonnegative",
    "check_paracomplete_consistency",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_PARACONSISTENT_SETS_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_PARACONSISTENT_SETS_001"]
