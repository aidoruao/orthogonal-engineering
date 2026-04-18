"""Implementation models for d_arxiv_quantum_error_correction_gkp."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumGKPErrorCorrectionClaim:
    """Structured claim parameters derived from arXiv paper 2604.08247v1 (quant-ph)."""

    squeezing_db: Fraction
    logical_error_rate: Fraction
    physical_error_rate: Fraction
    preprocessing_applied: bool
    code_distance: Fraction


def create_nominal_claim() -> QuantumGKPErrorCorrectionClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumGKPErrorCorrectionClaim(
        squeezing_db=Fraction(15),
        logical_error_rate=Fraction(1, 1000),
        physical_error_rate=Fraction(1, 100),
        preprocessing_applied=True,
        code_distance=Fraction(3),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_ERROR_CORRECTION_GKP",
    "paper_id": "2604.08247v1",
    "claim_model": "QuantumGKPErrorCorrectionClaim",
    "check_functions": [
        "check_error_rate_suppression",
        "check_squeezing_nonnegative",
        "check_physical_error_rate_valid",
        "check_logical_error_rate_valid",
        "check_code_distance_positive",
    ],
}
