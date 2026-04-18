"""Implementation models for d_arxiv_statml_conformal_margin."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ConformalMarginClaim:
    """Structured claim parameters derived from arXiv paper 2604.06468v2 (stat.ML)."""

    margin: Fraction
    noise_rate: Fraction
    coverage_guarantee: Fraction
    is_robust: bool
    risk_bound: Fraction


def create_nominal_claim() -> ConformalMarginClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ConformalMarginClaim(
        margin=Fraction(1, 4),
        noise_rate=Fraction(1, 5),
        coverage_guarantee=Fraction(9, 10),
        is_robust=True,
        risk_bound=Fraction(1, 10),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_CONFORMAL_MARGIN",
    "paper_id": "2604.06468v2",
    "claim_model": "ConformalMarginClaim",
    "check_functions": [
        "check_margin_positive",
        "check_noise_rate_valid",
        "check_coverage_valid",
        "check_robustness",
        "check_risk_bound_valid",
    ],
}
