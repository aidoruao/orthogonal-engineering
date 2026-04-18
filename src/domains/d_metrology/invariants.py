"""Invariant checks for Metrology."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import MetrologyClaim, create_nominal_claim


def check_measurement_traceability(data: MetrologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Measurement is traceable to standard.

    Standard: Metrology domain invariant.
    Falsifies if: not measurement_traceable.
    falsifies_if: not measurement_traceable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.measurement_traceable
    proof = ProofObject(
        rule="check_measurement_traceability",
        premises=[
            "domain=Metrology",
            f"measurement_traceable={{data.measurement_traceable}}",
        ],
        conclusion=(
            "PASS: Measurement is traceable to standard"
            if success else "FAIL: Measurement is traceable to standard"
        ),
    )
    return success, proof


def check_calibration_interval_valid(data: MetrologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Calibration interval is valid.

    Standard: Metrology domain invariant.
    Falsifies if: not calibration_interval_valid.
    falsifies_if: not calibration_interval_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.calibration_interval_valid
    proof = ProofObject(
        rule="check_calibration_interval_valid",
        premises=[
            "domain=Metrology",
            f"calibration_interval_valid={{data.calibration_interval_valid}}",
        ],
        conclusion=(
            "PASS: Calibration interval is valid"
            if success else "FAIL: Calibration interval is valid"
        ),
    )
    return success, proof


def check_measurement_uncertainty_quantified(data: MetrologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Measurement uncertainty is quantified.

    Standard: Metrology domain invariant.
    Falsifies if: not uncertainty_quantified.
    falsifies_if: not uncertainty_quantified.

    Returns:
        Tuple of (success, proof).
    """
    success = data.uncertainty_quantified
    proof = ProofObject(
        rule="check_measurement_uncertainty_quantified",
        premises=[
            "domain=Metrology",
            f"uncertainty_quantified={{data.uncertainty_quantified}}",
        ],
        conclusion=(
            "PASS: Measurement uncertainty is quantified"
            if success else "FAIL: Measurement uncertainty is quantified"
        ),
    )
    return success, proof


def check_repeatability_within_tolerance(data: MetrologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Repeatability is within tolerance.

    Standard: Metrology domain invariant.
    Falsifies if: not repeatability_within_tolerance.
    falsifies_if: not repeatability_within_tolerance.

    Returns:
        Tuple of (success, proof).
    """
    success = data.repeatability_within_tolerance
    proof = ProofObject(
        rule="check_repeatability_within_tolerance",
        premises=[
            "domain=Metrology",
            f"repeatability_within_tolerance={{data.repeatability_within_tolerance}}",
        ],
        conclusion=(
            "PASS: Repeatability is within tolerance"
            if success else "FAIL: Repeatability is within tolerance"
        ),
    )
    return success, proof


def check_resolution_ratio_fraction(data: MetrologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Resolution ratio is positive.

    Standard: Metrology domain invariant.
    Falsifies if: not resolution_ratio.
    falsifies_if: not resolution_ratio.

    Returns:
        Tuple of (success, proof).
    """
    success = data.resolution_ratio >= Fraction(0)
    proof = ProofObject(
        rule="check_resolution_ratio_fraction",
        premises=[
            "domain=Metrology",
            f"resolution_ratio={{data.resolution_ratio}}",
        ],
        conclusion=(
            "PASS: Resolution ratio is positive is non-negative"
            if success else "FAIL: Resolution ratio is positive is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Metrology nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_measurement_traceability", check_measurement_traceability),
        ("check_calibration_interval_valid", check_calibration_interval_valid),
        ("check_measurement_uncertainty_quantified", check_measurement_uncertainty_quantified),
        ("check_repeatability_within_tolerance", check_repeatability_within_tolerance),
        ("check_resolution_ratio_fraction", check_resolution_ratio_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
