"""D_ARXIV_TARSKIAN_TRUTH domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_TARSKIAN_TRUTH"
DOMAIN_NAME = "Arxiv Tarskian Truth Theories over Set Theory"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "math.LO",
    "paper:2604.03825v2",
]

INVARIANTS = [
    "check_object_theory_consistency",
    "check_truth_predicate_consistency",
    "check_tarski_biconditional",
    "check_compositionality",
    "check_axiom_count_positive",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_TARSKIAN_TRUTH_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_TARSKIAN_TRUTH_001"]
