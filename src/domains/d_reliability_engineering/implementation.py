"""Implementation models for Reliability Engineering."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ReliabilityClaim:
    """Structured claim parameters for Reliability Engineering domain invariants."""

    mtbf_positive: bool
    failure_rate_monotonic: bool
    redundancy_independent: bool
    weibull_shape_positive: bool
    availability: Fraction


def create_nominal_claim() -> ReliabilityClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ReliabilityClaim(
        mtbf_positive=True,
        failure_rate_monotonic=True,
        redundancy_independent=True,
        weibull_shape_positive=True,
        availability=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "RELIABILITY_ENGINEERING",
    "claim_model": "ReliabilityClaim",
    "check_functions": [
        "check_mtbf_positive",
        "check_failure_rate_monotonic",
        "check_redundancy_independence",
        "check_weibull_shape_positive",
        "check_availability_fraction",
    ],
}
