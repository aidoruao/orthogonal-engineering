"""Implementation models for Statistics."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class StatisticsClaim:
    """Structured claim parameters for Statistics domain invariants."""

    sample_variance_unbiased: bool
    confidence_interval_covers: bool
    test_size_valid: bool
    estimator_consistent: bool
    p_value: Fraction


def create_nominal_claim() -> StatisticsClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return StatisticsClaim(
        sample_variance_unbiased=True,
        confidence_interval_covers=True,
        test_size_valid=True,
        estimator_consistent=True,
        p_value=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "STATISTICS",
    "claim_model": "StatisticsClaim",
    "check_functions": [
        "check_sample_variance_unbiased",
        "check_confidence_interval_coverage",
        "check_hypothesis_test_size_valid",
        "check_estimator_consistent",
        "check_p_value_fraction",
    ],
}
