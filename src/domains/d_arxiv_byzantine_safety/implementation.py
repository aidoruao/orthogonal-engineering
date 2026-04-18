"""Implementation models for d_arxiv_byzantine_safety."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ByzantineSafetyClaim:
    """Structured claim parameters derived from arXiv paper 2604.03844v1 (cs.LO)."""

    total_nodes: Fraction
    faulty_nodes: Fraction
    safety_threshold: Fraction
    is_safe: bool
    is_live: bool
    quorum_size: Fraction


def create_nominal_claim() -> ByzantineSafetyClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ByzantineSafetyClaim(
        total_nodes=Fraction(10),
        faulty_nodes=Fraction(3),
        safety_threshold=Fraction(3),
        is_safe=True,
        is_live=True,
        quorum_size=Fraction(7),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_BYZANTINE_SAFETY",
    "paper_id": "2604.03844v1",
    "claim_model": "ByzantineSafetyClaim",
    "check_functions": [
        "check_byzantine_fault_tolerance",
        "check_safety_property",
        "check_liveness_property",
        "check_threshold_formula",
        "check_quorum_validity",
    ],
}
