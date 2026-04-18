"""Invariant checks for Manufacturing."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ManufacturingClaim, create_nominal_claim


def check_tolerance_stackup_valid(data: ManufacturingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Tolerance stack-up is valid.

    Standard: Manufacturing domain invariant.
    Falsifies if: not tolerance_stackup_valid.
    falsifies_if: not tolerance_stackup_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.tolerance_stackup_valid
    proof = ProofObject(
        rule="check_tolerance_stackup_valid",
        premises=[
            "domain=Manufacturing",
            f"tolerance_stackup_valid={{data.tolerance_stackup_valid}}",
        ],
        conclusion=(
            "PASS: Tolerance stack-up is valid"
            if success else "FAIL: Tolerance stack-up is valid"
        ),
    )
    return success, proof


def check_process_capability_index(data: ManufacturingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Process capability index is acceptable.

    Standard: Manufacturing domain invariant.
    Falsifies if: not cpk_acceptable.
    falsifies_if: not cpk_acceptable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.cpk_acceptable
    proof = ProofObject(
        rule="check_process_capability_index",
        premises=[
            "domain=Manufacturing",
            f"cpk_acceptable={{data.cpk_acceptable}}",
        ],
        conclusion=(
            "PASS: Process capability index is acceptable"
            if success else "FAIL: Process capability index is acceptable"
        ),
    )
    return success, proof


def check_surface_finish_within_spec(data: ManufacturingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Surface finish is within specification.

    Standard: Manufacturing domain invariant.
    Falsifies if: not surface_finish_within_spec.
    falsifies_if: not surface_finish_within_spec.

    Returns:
        Tuple of (success, proof).
    """
    success = data.surface_finish_within_spec
    proof = ProofObject(
        rule="check_surface_finish_within_spec",
        premises=[
            "domain=Manufacturing",
            f"surface_finish_within_spec={{data.surface_finish_within_spec}}",
        ],
        conclusion=(
            "PASS: Surface finish is within specification"
            if success else "FAIL: Surface finish is within specification"
        ),
    )
    return success, proof


def check_lead_time_non_negative(data: ManufacturingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Lead time is non-negative.

    Standard: Manufacturing domain invariant.
    Falsifies if: not lead_time_non_negative.
    falsifies_if: not lead_time_non_negative.

    Returns:
        Tuple of (success, proof).
    """
    success = data.lead_time_non_negative
    proof = ProofObject(
        rule="check_lead_time_non_negative",
        premises=[
            "domain=Manufacturing",
            f"lead_time_non_negative={{data.lead_time_non_negative}}",
        ],
        conclusion=(
            "PASS: Lead time is non-negative"
            if success else "FAIL: Lead time is non-negative"
        ),
    )
    return success, proof


def check_scrap_rate_fraction(data: ManufacturingClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Scrap rate is non-negative.

    Standard: Manufacturing domain invariant.
    Falsifies if: not scrap_rate.
    falsifies_if: not scrap_rate.

    Returns:
        Tuple of (success, proof).
    """
    success = data.scrap_rate >= Fraction(0)
    proof = ProofObject(
        rule="check_scrap_rate_fraction",
        premises=[
            "domain=Manufacturing",
            f"scrap_rate={{data.scrap_rate}}",
        ],
        conclusion=(
            "PASS: Scrap rate is non-negative is non-negative"
            if success else "FAIL: Scrap rate is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Manufacturing nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_tolerance_stackup_valid", check_tolerance_stackup_valid),
        ("check_process_capability_index", check_process_capability_index),
        ("check_surface_finish_within_spec", check_surface_finish_within_spec),
        ("check_lead_time_non_negative", check_lead_time_non_negative),
        ("check_scrap_rate_fraction", check_scrap_rate_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
