"""Implementation models for d_arxiv_quantum_ergodic_process."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumErgodicProcessClaim:
    """Structured claim parameters derived from arXiv paper 2604.09422v1 (quant-ph)."""

    period: Fraction
    convergence_rate: Fraction
    hilbert_space_dimension: Fraction
    is_ergodic: bool
    is_periodic: bool


def create_nominal_claim() -> QuantumErgodicProcessClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumErgodicProcessClaim(
        period=Fraction(2),
        convergence_rate=Fraction(1, 2),
        hilbert_space_dimension=Fraction(4),
        is_ergodic=True,
        is_periodic=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_ERGODIC_PROCESS",
    "paper_id": "2604.09422v1",
    "claim_model": "QuantumErgodicProcessClaim",
    "check_functions": [
        "check_ergodicity",
        "check_period_positive",
        "check_convergence_rate_valid",
        "check_dimension_valid",
        "check_periodicity_flag",
    ],
}
