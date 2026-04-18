"""Implementation models for Metrology."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MetrologyClaim:
    """Structured claim parameters for Metrology domain invariants."""

    measurement_traceable: bool
    calibration_interval_valid: bool
    uncertainty_quantified: bool
    repeatability_within_tolerance: bool
    resolution_ratio: Fraction


def create_nominal_claim() -> MetrologyClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return MetrologyClaim(
        measurement_traceable=True,
        calibration_interval_valid=True,
        uncertainty_quantified=True,
        repeatability_within_tolerance=True,
        resolution_ratio=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "METROLOGY",
    "claim_model": "MetrologyClaim",
    "check_functions": [
        "check_measurement_traceability",
        "check_calibration_interval_valid",
        "check_measurement_uncertainty_quantified",
        "check_repeatability_within_tolerance",
        "check_resolution_ratio_fraction",
    ],
}
