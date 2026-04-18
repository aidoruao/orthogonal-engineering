"""Implementation models for Thermodynamics."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ThermodynamicsClaim:
    """Structured claim parameters for Thermodynamics domain invariants."""

    entropy_increases: bool
    temperature_positive: bool
    carnot_efficiency_valid: bool
    heat_capacity_positive: bool
    pressure_equilibrium: Fraction


def create_nominal_claim() -> ThermodynamicsClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ThermodynamicsClaim(
        entropy_increases=True,
        temperature_positive=True,
        carnot_efficiency_valid=True,
        heat_capacity_positive=True,
        pressure_equilibrium=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "THERMODYNAMICS",
    "claim_model": "ThermodynamicsClaim",
    "check_functions": [
        "check_entropy_increase",
        "check_temperature_positive",
        "check_carnot_efficiency_bound",
        "check_heat_capacity_positive",
        "check_pressure_equilibrium_fraction",
    ],
}
