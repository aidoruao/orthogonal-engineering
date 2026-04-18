"""D_ARXIV_CONTRACT_DEDUCTION domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_CONTRACT_DEDUCTION"
DOMAIN_NAME = "Contract Satisfaction Proofs via Deductive System"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.LO",
    "paper:2604.09165v1",
]

INVARIANTS = [
    "check_contract_soundness",
    "check_precondition_required",
    "check_axiom_count_positive",
    "check_inference_steps_positive",
    "check_derivation_bound",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_CONTRACT_DEDUCTION_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_CONTRACT_DEDUCTION_001"]
