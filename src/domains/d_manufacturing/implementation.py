"""Implementation models for Manufacturing."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ManufacturingClaim:
    """Structured claim parameters for Manufacturing domain invariants."""

    tolerance_stackup_valid: bool
    cpk_acceptable: bool
    surface_finish_within_spec: bool
    lead_time_non_negative: bool
    scrap_rate: Fraction


def create_nominal_claim() -> ManufacturingClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ManufacturingClaim(
        tolerance_stackup_valid=True,
        cpk_acceptable=True,
        surface_finish_within_spec=True,
        lead_time_non_negative=True,
        scrap_rate=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "MANUFACTURING",
    "claim_model": "ManufacturingClaim",
    "check_functions": [
        "check_tolerance_stackup_valid",
        "check_process_capability_index",
        "check_surface_finish_within_spec",
        "check_lead_time_non_negative",
        "check_scrap_rate_fraction",
    ],
}
