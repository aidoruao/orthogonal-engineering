"""Implementation models for d_arxiv_deontic_stit."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DeonticSTITClaim:
    """Structured claim parameters derived from arXiv paper 2604.00967v1 (cs.LO)."""

    agent_can_perform_action: bool
    action_is_obligatory: bool
    stit_model_valid: bool
    ought_implies_can: bool
    alternative_count: Fraction


def create_nominal_claim() -> DeonticSTITClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return DeonticSTITClaim(
        agent_can_perform_action=True,
        action_is_obligatory=True,
        stit_model_valid=True,
        ought_implies_can=True,
        alternative_count=Fraction(3),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_DEONTIC_STIT",
    "paper_id": "2604.00967v1",
    "claim_model": "DeonticSTITClaim",
    "check_functions": [
        "check_ought_implies_can",
        "check_stit_model_validity",
        "check_oic_consistency",
        "check_alternatives_positive",
        "check_agency_requirement",
    ],
}
