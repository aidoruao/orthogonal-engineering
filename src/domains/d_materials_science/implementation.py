"""Implementation models for Materials Science."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MaterialsClaim:
    """Structured claim parameters for Materials Science domain invariants."""

    yield_strength_positive: bool
    fracture_toughness_valid: bool
    crystallographic_symmetry_conserved: bool
    diffusion_coefficient_positive: bool
    grain_size_microns: Fraction


def create_nominal_claim() -> MaterialsClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return MaterialsClaim(
        yield_strength_positive=True,
        fracture_toughness_valid=True,
        crystallographic_symmetry_conserved=True,
        diffusion_coefficient_positive=True,
        grain_size_microns=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "MATERIALS_SCIENCE",
    "claim_model": "MaterialsClaim",
    "check_functions": [
        "check_yield_strength_positive",
        "check_fracture_toughness_valid",
        "check_crystallographic_symmetry",
        "check_diffusion_coefficient_positive",
        "check_grain_size_fraction",
    ],
}
