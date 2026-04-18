"""Invariant checks for Music Theory."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import MusicTheoryClaim, create_nominal_claim


def check_interval_consonance_valid(data: MusicTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Interval consonance is valid.

    Standard: Music Theory domain invariant.
    Falsifies if: not interval_consonance_valid.
    falsifies_if: not interval_consonance_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.interval_consonance_valid
    proof = ProofObject(
        rule="check_interval_consonance_valid",
        premises=[
            "domain=Music Theory",
            f"interval_consonance_valid={{data.interval_consonance_valid}}",
        ],
        conclusion=(
            "PASS: Interval consonance is valid"
            if success else "FAIL: Interval consonance is valid"
        ),
    )
    return success, proof


def check_scale_periodicity_octave(data: MusicTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Scale is periodic at the octave.

    Standard: Music Theory domain invariant.
    Falsifies if: not scale_periodic_octave.
    falsifies_if: not scale_periodic_octave.

    Returns:
        Tuple of (success, proof).
    """
    success = data.scale_periodic_octave
    proof = ProofObject(
        rule="check_scale_periodicity_octave",
        premises=[
            "domain=Music Theory",
            f"scale_periodic_octave={{data.scale_periodic_octave}}",
        ],
        conclusion=(
            "PASS: Scale is periodic at the octave"
            if success else "FAIL: Scale is periodic at the octave"
        ),
    )
    return success, proof


def check_harmonic_series_overtones(data: MusicTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Harmonic series overtones are valid.

    Standard: Music Theory domain invariant.
    Falsifies if: not harmonic_series_valid.
    falsifies_if: not harmonic_series_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.harmonic_series_valid
    proof = ProofObject(
        rule="check_harmonic_series_overtones",
        premises=[
            "domain=Music Theory",
            f"harmonic_series_valid={{data.harmonic_series_valid}}",
        ],
        conclusion=(
            "PASS: Harmonic series overtones are valid"
            if success else "FAIL: Harmonic series overtones are valid"
        ),
    )
    return success, proof


def check_voice_leading_rules(data: MusicTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Voice leading follows rules.

    Standard: Music Theory domain invariant.
    Falsifies if: not voice_leading_valid.
    falsifies_if: not voice_leading_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.voice_leading_valid
    proof = ProofObject(
        rule="check_voice_leading_rules",
        premises=[
            "domain=Music Theory",
            f"voice_leading_valid={{data.voice_leading_valid}}",
        ],
        conclusion=(
            "PASS: Voice leading follows rules"
            if success else "FAIL: Voice leading follows rules"
        ),
    )
    return success, proof


def check_temperament_deviation_fraction(data: MusicTheoryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Temperament deviation is non-negative.

    Standard: Music Theory domain invariant.
    Falsifies if: not temperament_deviation_cents.
    falsifies_if: not temperament_deviation_cents.

    Returns:
        Tuple of (success, proof).
    """
    success = data.temperament_deviation_cents >= Fraction(0)
    proof = ProofObject(
        rule="check_temperament_deviation_fraction",
        premises=[
            "domain=Music Theory",
            f"temperament_deviation_cents={{data.temperament_deviation_cents}}",
        ],
        conclusion=(
            "PASS: Temperament deviation is non-negative is non-negative"
            if success else "FAIL: Temperament deviation is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Music Theory nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_interval_consonance_valid", check_interval_consonance_valid),
        ("check_scale_periodicity_octave", check_scale_periodicity_octave),
        ("check_harmonic_series_overtones", check_harmonic_series_overtones),
        ("check_voice_leading_rules", check_voice_leading_rules),
        ("check_temperament_deviation_fraction", check_temperament_deviation_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
