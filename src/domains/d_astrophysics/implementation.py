"""Implementation models for Astrophysics."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class AstrophysicsClaim:
    """Structured claim parameters for Astrophysics domain invariants."""

    stellar_evolution_valid: bool
    dark_matter_density_positive: bool
    gravitational_wave_detectable: bool
    inflation_consistent: bool
    thermonuclear_rate: Fraction


def create_nominal_claim() -> AstrophysicsClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return AstrophysicsClaim(
        stellar_evolution_valid=True,
        dark_matter_density_positive=True,
        gravitational_wave_detectable=True,
        inflation_consistent=True,
        thermonuclear_rate=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "ASTROPHYSICS",
    "claim_model": "AstrophysicsClaim",
    "check_functions": [
        "check_stellar_evolution_model",
        "check_dark_matter_density",
        "check_gravitational_wave_signature",
        "check_cosmic_inflation_consistency",
        "check_thermonuclear_rate_fraction",
    ],
}
