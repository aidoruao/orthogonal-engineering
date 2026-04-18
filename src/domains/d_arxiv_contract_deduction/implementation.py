"""Implementation models for d_arxiv_contract_deduction."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ContractDeductionClaim:
    """Structured claim parameters derived from arXiv paper 2604.09165v1 (cs.LO)."""

    precondition_satisfied: bool
    postcondition_derived: bool
    contract_axioms_used: Fraction
    inference_steps: Fraction
    is_sound: bool


def create_nominal_claim() -> ContractDeductionClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ContractDeductionClaim(
        precondition_satisfied=True,
        postcondition_derived=True,
        contract_axioms_used=Fraction(5),
        inference_steps=Fraction(12),
        is_sound=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_CONTRACT_DEDUCTION",
    "paper_id": "2604.09165v1",
    "claim_model": "ContractDeductionClaim",
    "check_functions": [
        "check_contract_soundness",
        "check_precondition_required",
        "check_axiom_count_positive",
        "check_inference_steps_positive",
        "check_derivation_bound",
    ],
}
