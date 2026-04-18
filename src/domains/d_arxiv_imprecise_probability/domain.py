"""D_ARXIV_IMPRECISE_PROBABILITY domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_IMPRECISE_PROBABILITY"
DOMAIN_NAME = "Imprecise Probability and Credal Sets"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2604.09272v1",
]

INVARIANTS = [
    "check_credal_interval_validity",
    "check_credal_set_nonempty",
    "check_scott_continuity",
    "check_domain_theoretic_bound",
    "check_vacuous_coherence",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_IMPRECISE_PROBABILITY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_IMPRECISE_PROBABILITY_001"]
