"""Invariant checks for Electromagnetism."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ElectromagnetismClaim, create_nominal_claim


def check_maxwell_equations_consistent(data: ElectromagnetismClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Maxwell's equations are self-consistent.

    Standard: Electromagnetism domain invariant.
    Falsifies if: not maxwell_consistent.
    falsifies_if: not maxwell_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.maxwell_consistent
    proof = ProofObject(
        rule="check_maxwell_equations_consistent",
        premises=[
            "domain=Electromagnetism",
            f"maxwell_consistent={{data.maxwell_consistent}}",
        ],
        conclusion=(
            "PASS: Maxwell's equations are self-consistent"
            if success else "FAIL: Maxwell's equations are self-consistent"
        ),
    )
    return success, proof


def check_gauss_law_divergence(data: ElectromagnetismClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Gauss's law divergence condition holds.

    Standard: Electromagnetism domain invariant.
    Falsifies if: not gauss_law_holds.
    falsifies_if: not gauss_law_holds.

    Returns:
        Tuple of (success, proof).
    """
    success = data.gauss_law_holds
    proof = ProofObject(
        rule="check_gauss_law_divergence",
        premises=[
            "domain=Electromagnetism",
            f"gauss_law_holds={{data.gauss_law_holds}}",
        ],
        conclusion=(
            "PASS: Gauss's law divergence condition holds"
            if success else "FAIL: Gauss's law divergence condition holds"
        ),
    )
    return success, proof


def check_faraday_induction_non_negative(data: ElectromagnetismClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Faraday induction magnitude is valid.

    Standard: Electromagnetism domain invariant.
    Falsifies if: not faraday_induction_valid.
    falsifies_if: not faraday_induction_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.faraday_induction_valid
    proof = ProofObject(
        rule="check_faraday_induction_non_negative",
        premises=[
            "domain=Electromagnetism",
            f"faraday_induction_valid={{data.faraday_induction_valid}}",
        ],
        conclusion=(
            "PASS: Faraday induction magnitude is valid"
            if success else "FAIL: Faraday induction magnitude is valid"
        ),
    )
    return success, proof


def check_poynting_vector_conservation(data: ElectromagnetismClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Poynting vector conservation holds.

    Standard: Electromagnetism domain invariant.
    Falsifies if: not poynting_conserved.
    falsifies_if: not poynting_conserved.

    Returns:
        Tuple of (success, proof).
    """
    success = data.poynting_conserved
    proof = ProofObject(
        rule="check_poynting_vector_conservation",
        premises=[
            "domain=Electromagnetism",
            f"poynting_conserved={{data.poynting_conserved}}",
        ],
        conclusion=(
            "PASS: Poynting vector conservation holds"
            if success else "FAIL: Poynting vector conservation holds"
        ),
    )
    return success, proof


def check_permittivity_fraction(data: ElectromagnetismClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Relative permittivity is positive.

    Standard: Electromagnetism domain invariant.
    Falsifies if: not permittivity_ratio.
    falsifies_if: not permittivity_ratio.

    Returns:
        Tuple of (success, proof).
    """
    success = data.permittivity_ratio >= Fraction(0)
    proof = ProofObject(
        rule="check_permittivity_fraction",
        premises=[
            "domain=Electromagnetism",
            f"permittivity_ratio={{data.permittivity_ratio}}",
        ],
        conclusion=(
            "PASS: Relative permittivity is positive is non-negative"
            if success else "FAIL: Relative permittivity is positive is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Electromagnetism nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_maxwell_equations_consistent", check_maxwell_equations_consistent),
        ("check_gauss_law_divergence", check_gauss_law_divergence),
        ("check_faraday_induction_non_negative", check_faraday_induction_non_negative),
        ("check_poynting_vector_conservation", check_poynting_vector_conservation),
        ("check_permittivity_fraction", check_permittivity_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
