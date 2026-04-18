"""Implementation models for Architecture Design."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ArchitectureDesignClaim:
    """Structured claim parameters for Architecture Design domain invariants."""

    structural_load_path_valid: bool
    spatial_program_adherent: bool
    circulation_accessible: bool
    daylight_factor_sufficient: bool
    floor_area_ratio: Fraction


def create_nominal_claim() -> ArchitectureDesignClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ArchitectureDesignClaim(
        structural_load_path_valid=True,
        spatial_program_adherent=True,
        circulation_accessible=True,
        daylight_factor_sufficient=True,
        floor_area_ratio=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "ARCHITECTURE_DESIGN",
    "claim_model": "ArchitectureDesignClaim",
    "check_functions": [
        "check_structural_load_path",
        "check_spatial_program_adherence",
        "check_circulation_accessibility",
        "check_daylight_factor_sufficient",
        "check_floor_area_ratio_fraction",
    ],
}
