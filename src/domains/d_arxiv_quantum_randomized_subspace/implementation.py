"""Implementation models for d_arxiv_quantum_randomized_subspace."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumRandomizedSubspaceClaim:
    """Structured claim parameters derived from arXiv paper 2604.09483v1 (quant-ph)."""

    subspace_dimension: Fraction
    ambient_dimension: Fraction
    iteration_count: Fraction
    spectral_gap: Fraction
    approximation_error: Fraction


def create_nominal_claim() -> QuantumRandomizedSubspaceClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumRandomizedSubspaceClaim(
        subspace_dimension=Fraction(5),
        ambient_dimension=Fraction(100),
        iteration_count=Fraction(10),
        spectral_gap=Fraction(1, 10),
        approximation_error=Fraction(1, 100),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE",
    "paper_id": "2604.09483v1",
    "claim_model": "QuantumRandomizedSubspaceClaim",
    "check_functions": [
        "check_subspace_dimension_valid",
        "check_spectral_gap_positive",
        "check_iteration_count_positive",
        "check_approximation_error_nonnegative",
        "check_ambient_dimension_positive",
    ],
}
