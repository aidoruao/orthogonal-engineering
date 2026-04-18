"""Invariant checks for Astrophysics."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import AstrophysicsClaim, create_nominal_claim


def check_stellar_evolution_model(data: AstrophysicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Stellar evolution model is physically valid.

    Standard: Astrophysics domain invariant.
    Falsifies if: not stellar_evolution_valid.
    falsifies_if: not stellar_evolution_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.stellar_evolution_valid
    proof = ProofObject(
        rule="check_stellar_evolution_model",
        premises=[
            "domain=Astrophysics",
            f"stellar_evolution_valid={{data.stellar_evolution_valid}}",
        ],
        conclusion=(
            "PASS: Stellar evolution model is physically valid"
            if success else "FAIL: Stellar evolution model is physically valid"
        ),
    )
    return success, proof


def check_dark_matter_density(data: AstrophysicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Dark matter density is positive.

    Standard: Astrophysics domain invariant.
    Falsifies if: not dark_matter_density_positive.
    falsifies_if: not dark_matter_density_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.dark_matter_density_positive
    proof = ProofObject(
        rule="check_dark_matter_density",
        premises=[
            "domain=Astrophysics",
            f"dark_matter_density_positive={{data.dark_matter_density_positive}}",
        ],
        conclusion=(
            "PASS: Dark matter density is positive"
            if success else "FAIL: Dark matter density is positive"
        ),
    )
    return success, proof


def check_gravitational_wave_signature(data: AstrophysicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Gravitational wave signature is detectable.

    Standard: Astrophysics domain invariant.
    Falsifies if: not gravitational_wave_detectable.
    falsifies_if: not gravitational_wave_detectable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.gravitational_wave_detectable
    proof = ProofObject(
        rule="check_gravitational_wave_signature",
        premises=[
            "domain=Astrophysics",
            f"gravitational_wave_detectable={{data.gravitational_wave_detectable}}",
        ],
        conclusion=(
            "PASS: Gravitational wave signature is detectable"
            if success else "FAIL: Gravitational wave signature is detectable"
        ),
    )
    return success, proof


def check_cosmic_inflation_consistency(data: AstrophysicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Cosmic inflation parameters are consistent.

    Standard: Astrophysics domain invariant.
    Falsifies if: not inflation_consistent.
    falsifies_if: not inflation_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.inflation_consistent
    proof = ProofObject(
        rule="check_cosmic_inflation_consistency",
        premises=[
            "domain=Astrophysics",
            f"inflation_consistent={{data.inflation_consistent}}",
        ],
        conclusion=(
            "PASS: Cosmic inflation parameters are consistent"
            if success else "FAIL: Cosmic inflation parameters are consistent"
        ),
    )
    return success, proof


def check_thermonuclear_rate_fraction(data: AstrophysicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Thermonuclear reaction rate is non-negative.

    Standard: Astrophysics domain invariant.
    Falsifies if: not thermonuclear_rate.
    falsifies_if: not thermonuclear_rate.

    Returns:
        Tuple of (success, proof).
    """
    success = data.thermonuclear_rate >= Fraction(0)
    proof = ProofObject(
        rule="check_thermonuclear_rate_fraction",
        premises=[
            "domain=Astrophysics",
            f"thermonuclear_rate={{data.thermonuclear_rate}}",
        ],
        conclusion=(
            "PASS: Thermonuclear reaction rate is non-negative is non-negative"
            if success else "FAIL: Thermonuclear reaction rate is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Astrophysics nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_stellar_evolution_model", check_stellar_evolution_model),
        ("check_dark_matter_density", check_dark_matter_density),
        ("check_gravitational_wave_signature", check_gravitational_wave_signature),
        ("check_cosmic_inflation_consistency", check_cosmic_inflation_consistency),
        ("check_thermonuclear_rate_fraction", check_thermonuclear_rate_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
