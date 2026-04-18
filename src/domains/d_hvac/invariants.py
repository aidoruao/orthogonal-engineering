"""Invariant checks for HVAC."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import HvacClaim, create_nominal_claim


def check_heat_load_calculated(data: HvacClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Heat load is calculated.

    Standard: HVAC domain invariant.
    Falsifies if: not heat_load_calculated.
    falsifies_if: not heat_load_calculated.

    Returns:
        Tuple of (success, proof).
    """
    success = data.heat_load_calculated
    proof = ProofObject(
        rule="check_heat_load_calculated",
        premises=[
            "domain=HVAC",
            f"heat_load_calculated={{data.heat_load_calculated}}",
        ],
        conclusion=(
            "PASS: Heat load is calculated"
            if success else "FAIL: Heat load is calculated"
        ),
    )
    return success, proof


def check_air_changes_per_hour_sufficient(data: HvacClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Air changes per hour are sufficient.

    Standard: HVAC domain invariant.
    Falsifies if: not ach_sufficient.
    falsifies_if: not ach_sufficient.

    Returns:
        Tuple of (success, proof).
    """
    success = data.ach_sufficient
    proof = ProofObject(
        rule="check_air_changes_per_hour_sufficient",
        premises=[
            "domain=HVAC",
            f"ach_sufficient={{data.ach_sufficient}}",
        ],
        conclusion=(
            "PASS: Air changes per hour are sufficient"
            if success else "FAIL: Air changes per hour are sufficient"
        ),
    )
    return success, proof


def check_refrigerant_charge_correct(data: HvacClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Refrigerant charge is correct.

    Standard: HVAC domain invariant.
    Falsifies if: not refrigerant_charge_correct.
    falsifies_if: not refrigerant_charge_correct.

    Returns:
        Tuple of (success, proof).
    """
    success = data.refrigerant_charge_correct
    proof = ProofObject(
        rule="check_refrigerant_charge_correct",
        premises=[
            "domain=HVAC",
            f"refrigerant_charge_correct={{data.refrigerant_charge_correct}}",
        ],
        conclusion=(
            "PASS: Refrigerant charge is correct"
            if success else "FAIL: Refrigerant charge is correct"
        ),
    )
    return success, proof


def check_duct_leakage_within_spec(data: HvacClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Duct leakage is within specification.

    Standard: HVAC domain invariant.
    Falsifies if: not duct_leakage_within_spec.
    falsifies_if: not duct_leakage_within_spec.

    Returns:
        Tuple of (success, proof).
    """
    success = data.duct_leakage_within_spec
    proof = ProofObject(
        rule="check_duct_leakage_within_spec",
        premises=[
            "domain=HVAC",
            f"duct_leakage_within_spec={{data.duct_leakage_within_spec}}",
        ],
        conclusion=(
            "PASS: Duct leakage is within specification"
            if success else "FAIL: Duct leakage is within specification"
        ),
    )
    return success, proof


def check_efficiency_seer_fraction(data: HvacClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Efficiency SEER is non-negative.

    Standard: HVAC domain invariant.
    Falsifies if: not efficiency_seer.
    falsifies_if: not efficiency_seer.

    Returns:
        Tuple of (success, proof).
    """
    success = data.efficiency_seer >= Fraction(0)
    proof = ProofObject(
        rule="check_efficiency_seer_fraction",
        premises=[
            "domain=HVAC",
            f"efficiency_seer={{data.efficiency_seer}}",
        ],
        conclusion=(
            "PASS: Efficiency SEER is non-negative is non-negative"
            if success else "FAIL: Efficiency SEER is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: HVAC nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_heat_load_calculated", check_heat_load_calculated),
        ("check_air_changes_per_hour_sufficient", check_air_changes_per_hour_sufficient),
        ("check_refrigerant_charge_correct", check_refrigerant_charge_correct),
        ("check_duct_leakage_within_spec", check_duct_leakage_within_spec),
        ("check_efficiency_seer_fraction", check_efficiency_seer_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
