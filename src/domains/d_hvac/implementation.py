"""Implementation models for HVAC."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class HvacClaim:
    """Structured claim parameters for HVAC domain invariants."""

    heat_load_calculated: bool
    ach_sufficient: bool
    refrigerant_charge_correct: bool
    duct_leakage_within_spec: bool
    efficiency_seer: Fraction


def create_nominal_claim() -> HvacClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return HvacClaim(
        heat_load_calculated=True,
        ach_sufficient=True,
        refrigerant_charge_correct=True,
        duct_leakage_within_spec=True,
        efficiency_seer=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "HVAC",
    "claim_model": "HvacClaim",
    "check_functions": [
        "check_heat_load_calculated",
        "check_air_changes_per_hour_sufficient",
        "check_refrigerant_charge_correct",
        "check_duct_leakage_within_spec",
        "check_efficiency_seer_fraction",
    ],
}
