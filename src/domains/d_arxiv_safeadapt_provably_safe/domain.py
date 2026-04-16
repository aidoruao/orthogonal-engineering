"""D_ARXIV_SAFEADAPT_PROVABLY_SAFE domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_SAFEADAPT_PROVABLY_SAFE"
DOMAIN_NAME = "Arxiv Safeadapt Provably Safe"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09452v1",
]

INVARIANTS = [
    "check_safety_constraint_preservation",
    "check_violation_probability_cap",
    "check_return_non_degradation",
    "check_formal_margin_positive",
    "check_shift_resilience_floor",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_SAFEADAPT_PROVABLY_SAFE_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_SAFEADAPT_PROVABLY_SAFE_001"]
