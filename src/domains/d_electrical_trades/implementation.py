"""Implementation models for Electrical Trades."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ElectricalTradesClaim:
    """Structured claim parameters for Electrical Trades domain invariants."""

    ohms_law_satisfied: bool
    ground_fault_protected: bool
    conductor_ampacity_sufficient: bool
    arc_flash_boundary_calculated: bool
    voltage_drop_percent: Fraction


def create_nominal_claim() -> ElectricalTradesClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ElectricalTradesClaim(
        ohms_law_satisfied=True,
        ground_fault_protected=True,
        conductor_ampacity_sufficient=True,
        arc_flash_boundary_calculated=True,
        voltage_drop_percent=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "ELECTRICAL_TRADES",
    "claim_model": "ElectricalTradesClaim",
    "check_functions": [
        "check_ohms_law_satisfied",
        "check_ground_fault_protection",
        "check_conductor_ampacity_sufficient",
        "check_arc_flash_boundary_calculated",
        "check_voltage_drop_fraction",
    ],
}
