"""Implementation models for d_arxiv_quantum_uncertainty_entropy."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumUncertaintyEntropyClaim:
    """Structured claim parameters derived from arXiv paper 2604.09384v1 (quant-ph)."""

    von_neumann_entropy: Fraction
    purity: Fraction
    dimension: Fraction
    min_entropy: Fraction
    uncertainty_lower_bound: Fraction


def create_nominal_claim() -> QuantumUncertaintyEntropyClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumUncertaintyEntropyClaim(
        von_neumann_entropy=Fraction(1),
        purity=Fraction(1, 2),
        dimension=Fraction(4),
        min_entropy=Fraction(1, 2),
        uncertainty_lower_bound=Fraction(1, 4),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_UNCERTAINTY_ENTROPY",
    "paper_id": "2604.09384v1",
    "claim_model": "QuantumUncertaintyEntropyClaim",
    "check_functions": [
        "check_von_neumann_nonnegative",
        "check_purity_valid",
        "check_entropy_purity_tradeoff",
        "check_min_entropy_nonnegative",
        "check_uncertainty_lower_bound",
    ],
}
