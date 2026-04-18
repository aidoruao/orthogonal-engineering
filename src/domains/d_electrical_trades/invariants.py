"""Invariant checks for Electrical Trades."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ElectricalTradesClaim, create_nominal_claim


def check_ohms_law_satisfied(data: ElectricalTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Ohm's law is satisfied.

    Standard: Electrical Trades domain invariant.
    Falsifies if: not ohms_law_satisfied.
    falsifies_if: not ohms_law_satisfied.

    Returns:
        Tuple of (success, proof).
    """
    success = data.ohms_law_satisfied
    proof = ProofObject(
        rule="check_ohms_law_satisfied",
        premises=[
            "domain=Electrical Trades",
            f"ohms_law_satisfied={{data.ohms_law_satisfied}}",
        ],
        conclusion=(
            "PASS: Ohm's law is satisfied"
            if success else "FAIL: Ohm's law is satisfied"
        ),
    )
    return success, proof


def check_ground_fault_protection(data: ElectricalTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Ground fault protection is present.

    Standard: Electrical Trades domain invariant.
    Falsifies if: not ground_fault_protected.
    falsifies_if: not ground_fault_protected.

    Returns:
        Tuple of (success, proof).
    """
    success = data.ground_fault_protected
    proof = ProofObject(
        rule="check_ground_fault_protection",
        premises=[
            "domain=Electrical Trades",
            f"ground_fault_protected={{data.ground_fault_protected}}",
        ],
        conclusion=(
            "PASS: Ground fault protection is present"
            if success else "FAIL: Ground fault protection is present"
        ),
    )
    return success, proof


def check_conductor_ampacity_sufficient(data: ElectricalTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Conductor ampacity is sufficient for load.

    Standard: Electrical Trades domain invariant.
    Falsifies if: not conductor_ampacity_sufficient.
    falsifies_if: not conductor_ampacity_sufficient.

    Returns:
        Tuple of (success, proof).
    """
    success = data.conductor_ampacity_sufficient
    proof = ProofObject(
        rule="check_conductor_ampacity_sufficient",
        premises=[
            "domain=Electrical Trades",
            f"conductor_ampacity_sufficient={{data.conductor_ampacity_sufficient}}",
        ],
        conclusion=(
            "PASS: Conductor ampacity is sufficient for load"
            if success else "FAIL: Conductor ampacity is sufficient for load"
        ),
    )
    return success, proof


def check_arc_flash_boundary_calculated(data: ElectricalTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Arc flash boundary is calculated.

    Standard: Electrical Trades domain invariant.
    Falsifies if: not arc_flash_boundary_calculated.
    falsifies_if: not arc_flash_boundary_calculated.

    Returns:
        Tuple of (success, proof).
    """
    success = data.arc_flash_boundary_calculated
    proof = ProofObject(
        rule="check_arc_flash_boundary_calculated",
        premises=[
            "domain=Electrical Trades",
            f"arc_flash_boundary_calculated={{data.arc_flash_boundary_calculated}}",
        ],
        conclusion=(
            "PASS: Arc flash boundary is calculated"
            if success else "FAIL: Arc flash boundary is calculated"
        ),
    )
    return success, proof


def check_voltage_drop_fraction(data: ElectricalTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Voltage drop percentage is non-negative.

    Standard: Electrical Trades domain invariant.
    Falsifies if: not voltage_drop_percent.
    falsifies_if: not voltage_drop_percent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.voltage_drop_percent >= Fraction(0)
    proof = ProofObject(
        rule="check_voltage_drop_fraction",
        premises=[
            "domain=Electrical Trades",
            f"voltage_drop_percent={{data.voltage_drop_percent}}",
        ],
        conclusion=(
            "PASS: Voltage drop percentage is non-negative is non-negative"
            if success else "FAIL: Voltage drop percentage is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Electrical Trades nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_ohms_law_satisfied", check_ohms_law_satisfied),
        ("check_ground_fault_protection", check_ground_fault_protection),
        ("check_conductor_ampacity_sufficient", check_conductor_ampacity_sufficient),
        ("check_arc_flash_boundary_calculated", check_arc_flash_boundary_calculated),
        ("check_voltage_drop_fraction", check_voltage_drop_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
