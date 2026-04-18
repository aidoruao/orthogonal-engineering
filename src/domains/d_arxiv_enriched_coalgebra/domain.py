"""D_ARXIV_ENRICHED_COALGEBRA domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_ENRICHED_COALGEBRA"
DOMAIN_NAME = "Arxiv Enriched Coalgebras are Sometimes Comonadic"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.CT",
    "paper:2604.09354v1",
]

INVARIANTS = [
    "check_comonadicity",
    "check_comonad_existence",
    "check_comparison_equivalence",
    "check_base_category_nonempty",
    "check_enrichment_nonempty",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_ENRICHED_COALGEBRA_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_ENRICHED_COALGEBRA_001"]
