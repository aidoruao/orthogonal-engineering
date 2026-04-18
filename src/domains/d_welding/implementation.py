"""Implementation models for Welding."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class WeldingClaim:
    """Structured claim parameters for Welding domain invariants."""

    weld_penetration_adequate: bool
    haz_bounded: bool
    filler_compatible: bool
    wps_followed: bool
    weld_strength_ksi: Fraction


def create_nominal_claim() -> WeldingClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return WeldingClaim(
        weld_penetration_adequate=True,
        haz_bounded=True,
        filler_compatible=True,
        wps_followed=True,
        weld_strength_ksi=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "WELDING",
    "claim_model": "WeldingClaim",
    "check_functions": [
        "check_weld_penetration_adequate",
        "check_heat_affected_zone_bounded",
        "check_filler_material_compatible",
        "check_wps_followed",
        "check_weld_strength_fraction",
    ],
}
