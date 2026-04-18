"""Implementation models for d_arxiv_quantum_nonlocal_games."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumNonlocalGameClaim:
    """Structured claim parameters derived from arXiv paper 2604.09458v1 (quant-ph)."""

    classical_winning_probability: Fraction
    quantum_winning_probability: Fraction
    is_quantum_advantage: bool
    entanglement_dimension: Fraction
    is_pseudo_telepathy: bool


def create_nominal_claim() -> QuantumNonlocalGameClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumNonlocalGameClaim(
        classical_winning_probability=Fraction(3, 4),
        quantum_winning_probability=Fraction(1),
        is_quantum_advantage=True,
        entanglement_dimension=Fraction(2),
        is_pseudo_telepathy=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_NONLOCAL_GAMES",
    "paper_id": "2604.09458v1",
    "claim_model": "QuantumNonlocalGameClaim",
    "check_functions": [
        "check_classical_probability_valid",
        "check_quantum_probability_valid",
        "check_quantum_advantage",
        "check_entanglement_dimension_positive",
        "check_pseudo_telepathy_consistency",
    ],
}
