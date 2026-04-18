"""Implementation models for Formal Logic."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class FormalLogicClaim:
    """Structured claim parameters for Formal Logic domain invariants."""

    soundness_holds: bool
    completeness_holds: bool
    consistent_no_contradiction: bool
    decidability_defined: bool
    proof_length: Fraction


def create_nominal_claim() -> FormalLogicClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return FormalLogicClaim(
        soundness_holds=True,
        completeness_holds=True,
        consistent_no_contradiction=True,
        decidability_defined=True,
        proof_length=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "FORMAL_LOGIC",
    "claim_model": "FormalLogicClaim",
    "check_functions": [
        "check_soundness_theorem_holds",
        "check_completeness_theorem_holds",
        "check_consistency_no_contradiction",
        "check_decidability_defined",
        "check_proof_length_fraction",
    ],
}
