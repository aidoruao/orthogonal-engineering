"""Implementation models for d_arxiv_statml_conformal_prediction."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ConformalPredictionClaim:
    """Structured claim parameters derived from arXiv paper 2604.07325v1 (stat.ML)."""

    coverage_level: Fraction
    empirical_coverage: Fraction
    alpha: Fraction
    exchangeability_satisfied: bool
    prediction_set_size: Fraction


def create_nominal_claim() -> ConformalPredictionClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return ConformalPredictionClaim(
        coverage_level=Fraction(9, 10),
        empirical_coverage=Fraction(91, 100),
        alpha=Fraction(1, 10),
        exchangeability_satisfied=True,
        prediction_set_size=Fraction(5),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_CONFORMAL_PREDICTION",
    "paper_id": "2604.07325v1",
    "claim_model": "ConformalPredictionClaim",
    "check_functions": [
        "check_coverage_guarantee",
        "check_alpha_valid",
        "check_coverage_level_consistency",
        "check_exchangeability",
        "check_prediction_set_size_positive",
    ],
}
