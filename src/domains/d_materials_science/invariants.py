"""Invariant checks for Materials Science."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import MaterialsClaim, create_nominal_claim


def check_yield_strength_positive(data: MaterialsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Yield strength is positive.

    Standard: Materials Science domain invariant.
    Falsifies if: not yield_strength_positive.
    falsifies_if: not yield_strength_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.yield_strength_positive
    proof = ProofObject(
        rule="check_yield_strength_positive",
        premises=[
            "domain=Materials Science",
            f"yield_strength_positive={{data.yield_strength_positive}}",
        ],
        conclusion=(
            "PASS: Yield strength is positive"
            if success else "FAIL: Yield strength is positive"
        ),
    )
    return success, proof


def check_fracture_toughness_valid(data: MaterialsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Fracture toughness is within valid range.

    Standard: Materials Science domain invariant.
    Falsifies if: not fracture_toughness_valid.
    falsifies_if: not fracture_toughness_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.fracture_toughness_valid
    proof = ProofObject(
        rule="check_fracture_toughness_valid",
        premises=[
            "domain=Materials Science",
            f"fracture_toughness_valid={{data.fracture_toughness_valid}}",
        ],
        conclusion=(
            "PASS: Fracture toughness is within valid range"
            if success else "FAIL: Fracture toughness is within valid range"
        ),
    )
    return success, proof


def check_crystallographic_symmetry(data: MaterialsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Crystallographic symmetry is conserved.

    Standard: Materials Science domain invariant.
    Falsifies if: not crystallographic_symmetry_conserved.
    falsifies_if: not crystallographic_symmetry_conserved.

    Returns:
        Tuple of (success, proof).
    """
    success = data.crystallographic_symmetry_conserved
    proof = ProofObject(
        rule="check_crystallographic_symmetry",
        premises=[
            "domain=Materials Science",
            f"crystallographic_symmetry_conserved={{data.crystallographic_symmetry_conserved}}",
        ],
        conclusion=(
            "PASS: Crystallographic symmetry is conserved"
            if success else "FAIL: Crystallographic symmetry is conserved"
        ),
    )
    return success, proof


def check_diffusion_coefficient_positive(data: MaterialsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Diffusion coefficient is positive.

    Standard: Materials Science domain invariant.
    Falsifies if: not diffusion_coefficient_positive.
    falsifies_if: not diffusion_coefficient_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.diffusion_coefficient_positive
    proof = ProofObject(
        rule="check_diffusion_coefficient_positive",
        premises=[
            "domain=Materials Science",
            f"diffusion_coefficient_positive={{data.diffusion_coefficient_positive}}",
        ],
        conclusion=(
            "PASS: Diffusion coefficient is positive"
            if success else "FAIL: Diffusion coefficient is positive"
        ),
    )
    return success, proof


def check_grain_size_fraction(data: MaterialsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Grain size is positive.

    Standard: Materials Science domain invariant.
    Falsifies if: not grain_size_microns.
    falsifies_if: not grain_size_microns.

    Returns:
        Tuple of (success, proof).
    """
    success = data.grain_size_microns >= Fraction(0)
    proof = ProofObject(
        rule="check_grain_size_fraction",
        premises=[
            "domain=Materials Science",
            f"grain_size_microns={{data.grain_size_microns}}",
        ],
        conclusion=(
            "PASS: Grain size is positive is non-negative"
            if success else "FAIL: Grain size is positive is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Materials Science nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_yield_strength_positive", check_yield_strength_positive),
        ("check_fracture_toughness_valid", check_fracture_toughness_valid),
        ("check_crystallographic_symmetry", check_crystallographic_symmetry),
        ("check_diffusion_coefficient_positive", check_diffusion_coefficient_positive),
        ("check_grain_size_fraction", check_grain_size_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
