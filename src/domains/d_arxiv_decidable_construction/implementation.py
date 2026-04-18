"""Implementation models for d_arxiv_decidable_construction."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DecidableConstructionClaim:
    """Structured claim parameters derived from arXiv paper 2603.25414v1 (cs.LO)."""

    property_is_decidable: bool
    verified_at_design_time: bool
    verification_steps: Fraction
    soundness_guaranteed: bool
    completeness_guaranteed: bool


def create_nominal_claim() -> DecidableConstructionClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return DecidableConstructionClaim(
        property_is_decidable=True,
        verified_at_design_time=True,
        verification_steps=Fraction(42),
        soundness_guaranteed=True,
        completeness_guaranteed=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_DECIDABLE_CONSTRUCTION",
    "paper_id": "2603.25414v1",
    "claim_model": "DecidableConstructionClaim",
    "check_functions": [
        "check_decidability",
        "check_design_time_verification",
        "check_soundness",
        "check_completeness",
        "check_verification_steps_positive",
    ],
}
