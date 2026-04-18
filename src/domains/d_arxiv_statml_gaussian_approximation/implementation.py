"""Implementation models for d_arxiv_statml_gaussian_approximation."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class GaussianApproximationClaim:
    """Structured claim parameters derived from arXiv paper 2604.07323v1 (stat.ML)."""

    sample_count: Fraction
    dimension: Fraction
    approximation_error: Fraction
    convergence_rate: Fraction
    is_asymptotically_normal: bool


def create_nominal_claim() -> GaussianApproximationClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return GaussianApproximationClaim(
        sample_count=Fraction(1000),
        dimension=Fraction(10),
        approximation_error=Fraction(1, 100),
        convergence_rate=Fraction(1, 32),
        is_asymptotically_normal=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_GAUSSIAN_APPROXIMATION",
    "paper_id": "2604.07323v1",
    "claim_model": "GaussianApproximationClaim",
    "check_functions": [
        "check_asymptotic_normality",
        "check_sample_count_positive",
        "check_approximation_error_valid",
        "check_convergence_rate_positive",
        "check_dimension_positive",
    ],
}
