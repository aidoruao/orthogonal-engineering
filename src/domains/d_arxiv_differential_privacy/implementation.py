"""Implementation models for d_arxiv_differential_privacy."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DifferentialPrivacyClaim:
    """Structured claim parameters derived from arXiv paper 2603.26215v2 (cs.LO)."""

    epsilon: Fraction
    delta: Fraction
    sensitivity: Fraction
    noise_scale: Fraction
    supermartingale_verified: bool


def create_nominal_claim() -> DifferentialPrivacyClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return DifferentialPrivacyClaim(
        epsilon=Fraction(1, 1),
        delta=Fraction(1, 1000000),
        sensitivity=Fraction(1),
        noise_scale=Fraction(1),
        supermartingale_verified=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_DIFFERENTIAL_PRIVACY",
    "paper_id": "2603.26215v2",
    "claim_model": "DifferentialPrivacyClaim",
    "check_functions": [
        "check_epsilon_nonnegative",
        "check_delta_in_range",
        "check_noise_sufficient",
        "check_supermartingale_certificate",
        "check_privacy_budget_positive",
    ],
}
