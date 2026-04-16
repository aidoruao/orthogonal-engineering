"""D_ARXIV_CASE_GROUNDED_EVIDENCE domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_CASE_GROUNDED_EVIDENCE"
DOMAIN_NAME = "Arxiv Case Grounded Evidence"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09537v1",
]

INVARIANTS = [
    "check_case_support_coverage",
    "check_evidence_sensitivity",
    "check_counterfactual_consistency",
    "check_retrieval_leakage_control",
    "check_evidence_conditioning_gain",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_CASE_GROUNDED_EVIDENCE_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_CASE_GROUNDED_EVIDENCE_001"]
