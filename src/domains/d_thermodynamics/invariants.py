"""Invariant checks for Thermodynamics."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ThermodynamicsClaim, create_nominal_claim


def check_entropy_increase(data: ThermodynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Entropy increases for irreversible processes.

    Standard: Thermodynamics domain invariant.
    Falsifies if: not entropy_increases.
    falsifies_if: not entropy_increases.

    Returns:
        Tuple of (success, proof).
    """
    success = data.entropy_increases
    proof = ProofObject(
        rule="check_entropy_increase",
        premises=[
            "domain=Thermodynamics",
            f"entropy_increases={{data.entropy_increases}}",
        ],
        conclusion=(
            "PASS: Entropy increases for irreversible processes"
            if success else "FAIL: Entropy increases for irreversible processes"
        ),
    )
    return success, proof


def check_temperature_positive(data: ThermodynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Absolute temperature is positive.

    Standard: Thermodynamics domain invariant.
    Falsifies if: not temperature_positive.
    falsifies_if: not temperature_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.temperature_positive
    proof = ProofObject(
        rule="check_temperature_positive",
        premises=[
            "domain=Thermodynamics",
            f"temperature_positive={{data.temperature_positive}}",
        ],
        conclusion=(
            "PASS: Absolute temperature is positive"
            if success else "FAIL: Absolute temperature is positive"
        ),
    )
    return success, proof


def check_carnot_efficiency_bound(data: ThermodynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Carnot efficiency does not exceed unity.

    Standard: Thermodynamics domain invariant.
    Falsifies if: not carnot_efficiency_valid.
    falsifies_if: not carnot_efficiency_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.carnot_efficiency_valid
    proof = ProofObject(
        rule="check_carnot_efficiency_bound",
        premises=[
            "domain=Thermodynamics",
            f"carnot_efficiency_valid={{data.carnot_efficiency_valid}}",
        ],
        conclusion=(
            "PASS: Carnot efficiency does not exceed unity"
            if success else "FAIL: Carnot efficiency does not exceed unity"
        ),
    )
    return success, proof


def check_heat_capacity_positive(data: ThermodynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Heat capacity is positive.

    Standard: Thermodynamics domain invariant.
    Falsifies if: not heat_capacity_positive.
    falsifies_if: not heat_capacity_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.heat_capacity_positive
    proof = ProofObject(
        rule="check_heat_capacity_positive",
        premises=[
            "domain=Thermodynamics",
            f"heat_capacity_positive={{data.heat_capacity_positive}}",
        ],
        conclusion=(
            "PASS: Heat capacity is positive"
            if success else "FAIL: Heat capacity is positive"
        ),
    )
    return success, proof


def check_pressure_equilibrium_fraction(data: ThermodynamicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Pressure equilibrium deviation is non-negative.

    Standard: Thermodynamics domain invariant.
    Falsifies if: not pressure_equilibrium.
    falsifies_if: not pressure_equilibrium.

    Returns:
        Tuple of (success, proof).
    """
    success = data.pressure_equilibrium >= Fraction(0)
    proof = ProofObject(
        rule="check_pressure_equilibrium_fraction",
        premises=[
            "domain=Thermodynamics",
            f"pressure_equilibrium={{data.pressure_equilibrium}}",
        ],
        conclusion=(
            "PASS: Pressure equilibrium deviation is non-negative is non-negative"
            if success else "FAIL: Pressure equilibrium deviation is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Thermodynamics nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_entropy_increase", check_entropy_increase),
        ("check_temperature_positive", check_temperature_positive),
        ("check_carnot_efficiency_bound", check_carnot_efficiency_bound),
        ("check_heat_capacity_positive", check_heat_capacity_positive),
        ("check_pressure_equilibrium_fraction", check_pressure_equilibrium_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
