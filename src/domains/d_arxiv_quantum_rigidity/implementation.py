"""Implementation models for d_arxiv_quantum_rigidity."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class CHSHRigidityClaim:
    """Structured claim parameters derived from arXiv paper 2604.03884v1 (cs.LO)."""

    chsh_value: Fraction
    quantum_max: Fraction
    is_quantum_strategy: bool
    entanglement_used: bool
    is_rigid: bool


def create_nominal_claim() -> CHSHRigidityClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return CHSHRigidityClaim(
        chsh_value=Fraction(28284, 10000),
        quantum_max=Fraction(28284, 10000),
        is_quantum_strategy=True,
        entanglement_used=True,
        is_rigid=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_RIGIDITY",
    "paper_id": "2604.03884v1",
    "claim_model": "CHSHRigidityClaim",
    "check_functions": [
        "check_chsh_classical_bound",
        "check_chsh_quantum_bound",
        "check_quantum_requires_entanglement",
        "check_rigidity",
        "check_quantum_advantage",
    ],
}
