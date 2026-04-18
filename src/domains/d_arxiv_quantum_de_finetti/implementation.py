"""Implementation models for d_arxiv_quantum_de_finetti."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumDeFinettiClaim:
    """Structured claim parameters derived from arXiv paper 2604.09410v1 (quant-ph)."""

    party_count: Fraction
    subsystem_count: Fraction
    de_finetti_error: Fraction
    dimension: Fraction
    is_exchangeable: bool


def create_nominal_claim() -> QuantumDeFinettiClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumDeFinettiClaim(
        party_count=Fraction(10),
        subsystem_count=Fraction(3),
        de_finetti_error=Fraction(1, 100),
        dimension=Fraction(2),
        is_exchangeable=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_DE_FINETTI",
    "paper_id": "2604.09410v1",
    "claim_model": "QuantumDeFinettiClaim",
    "check_functions": [
        "check_exchangeability",
        "check_subsystem_count_valid",
        "check_de_finetti_error_nonnegative",
        "check_dimension_positive",
        "check_party_count_positive",
    ],
}
