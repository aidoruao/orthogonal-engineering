"""D_ARXIV_STATML_PROXY_CAUSAL domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_STATML_PROXY_CAUSAL"
DOMAIN_NAME = "Arxiv StatML Proxy Causal"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "stat.ML",
    "paper:2604.09135v1",
]

INVARIANTS = [
    "check_identifiability",
    "check_consistency",
    "check_proxy_relevance_valid",
    "check_proxy_count_positive",
    "check_confounder_count_nonnegative",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_STATML_PROXY_CAUSAL_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_STATML_PROXY_CAUSAL_001"]
