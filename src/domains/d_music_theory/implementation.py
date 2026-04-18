"""Implementation models for Music Theory."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MusicTheoryClaim:
    """Structured claim parameters for Music Theory domain invariants."""

    interval_consonance_valid: bool
    scale_periodic_octave: bool
    harmonic_series_valid: bool
    voice_leading_valid: bool
    temperament_deviation_cents: Fraction


def create_nominal_claim() -> MusicTheoryClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return MusicTheoryClaim(
        interval_consonance_valid=True,
        scale_periodic_octave=True,
        harmonic_series_valid=True,
        voice_leading_valid=True,
        temperament_deviation_cents=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "MUSIC_THEORY",
    "claim_model": "MusicTheoryClaim",
    "check_functions": [
        "check_interval_consonance_valid",
        "check_scale_periodicity_octave",
        "check_harmonic_series_overtones",
        "check_voice_leading_rules",
        "check_temperament_deviation_fraction",
    ],
}
