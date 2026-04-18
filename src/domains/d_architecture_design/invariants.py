"""Invariant checks for Architecture Design."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ArchitectureDesignClaim, create_nominal_claim


def check_structural_load_path(data: ArchitectureDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Structural load path is valid.

    Standard: Architecture Design domain invariant.
    Falsifies if: not structural_load_path_valid.
    falsifies_if: not structural_load_path_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.structural_load_path_valid
    proof = ProofObject(
        rule="check_structural_load_path",
        premises=[
            "domain=Architecture Design",
            f"structural_load_path_valid={{data.structural_load_path_valid}}",
        ],
        conclusion=(
            "PASS: Structural load path is valid"
            if success else "FAIL: Structural load path is valid"
        ),
    )
    return success, proof


def check_spatial_program_adherence(data: ArchitectureDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Spatial program is adhered to.

    Standard: Architecture Design domain invariant.
    Falsifies if: not spatial_program_adherent.
    falsifies_if: not spatial_program_adherent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.spatial_program_adherent
    proof = ProofObject(
        rule="check_spatial_program_adherence",
        premises=[
            "domain=Architecture Design",
            f"spatial_program_adherent={{data.spatial_program_adherent}}",
        ],
        conclusion=(
            "PASS: Spatial program is adhered to"
            if success else "FAIL: Spatial program is adhered to"
        ),
    )
    return success, proof


def check_circulation_accessibility(data: ArchitectureDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Circulation is accessible.

    Standard: Architecture Design domain invariant.
    Falsifies if: not circulation_accessible.
    falsifies_if: not circulation_accessible.

    Returns:
        Tuple of (success, proof).
    """
    success = data.circulation_accessible
    proof = ProofObject(
        rule="check_circulation_accessibility",
        premises=[
            "domain=Architecture Design",
            f"circulation_accessible={{data.circulation_accessible}}",
        ],
        conclusion=(
            "PASS: Circulation is accessible"
            if success else "FAIL: Circulation is accessible"
        ),
    )
    return success, proof


def check_daylight_factor_sufficient(data: ArchitectureDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Daylight factor is sufficient.

    Standard: Architecture Design domain invariant.
    Falsifies if: not daylight_factor_sufficient.
    falsifies_if: not daylight_factor_sufficient.

    Returns:
        Tuple of (success, proof).
    """
    success = data.daylight_factor_sufficient
    proof = ProofObject(
        rule="check_daylight_factor_sufficient",
        premises=[
            "domain=Architecture Design",
            f"daylight_factor_sufficient={{data.daylight_factor_sufficient}}",
        ],
        conclusion=(
            "PASS: Daylight factor is sufficient"
            if success else "FAIL: Daylight factor is sufficient"
        ),
    )
    return success, proof


def check_floor_area_ratio_fraction(data: ArchitectureDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Floor area ratio is non-negative.

    Standard: Architecture Design domain invariant.
    Falsifies if: not floor_area_ratio.
    falsifies_if: not floor_area_ratio.

    Returns:
        Tuple of (success, proof).
    """
    success = data.floor_area_ratio >= Fraction(0)
    proof = ProofObject(
        rule="check_floor_area_ratio_fraction",
        premises=[
            "domain=Architecture Design",
            f"floor_area_ratio={{data.floor_area_ratio}}",
        ],
        conclusion=(
            "PASS: Floor area ratio is non-negative is non-negative"
            if success else "FAIL: Floor area ratio is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Architecture Design nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_structural_load_path", check_structural_load_path),
        ("check_spatial_program_adherence", check_spatial_program_adherence),
        ("check_circulation_accessibility", check_circulation_accessibility),
        ("check_daylight_factor_sufficient", check_daylight_factor_sufficient),
        ("check_floor_area_ratio_fraction", check_floor_area_ratio_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
