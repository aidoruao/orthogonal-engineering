"""Invariant checks for Political Philosophy."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import PoliticalPhilosophyClaim, create_nominal_claim


def check_social_contract_consensual(data: PoliticalPhilosophyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Social contract is consensual.

    Standard: Political Philosophy domain invariant.
    Falsifies if: not social_contract_consensual.
    falsifies_if: not social_contract_consensual.

    Returns:
        Tuple of (success, proof).
    """
    success = data.social_contract_consensual
    proof = ProofObject(
        rule="check_social_contract_consensual",
        premises=[
            "domain=Political Philosophy",
            f"social_contract_consensual={{data.social_contract_consensual}}",
        ],
        conclusion=(
            "PASS: Social contract is consensual"
            if success else "FAIL: Social contract is consensual"
        ),
    )
    return success, proof


def check_rights_non_derogable(data: PoliticalPhilosophyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Fundamental rights are non-derogable.

    Standard: Political Philosophy domain invariant.
    Falsifies if: not rights_non_derogable.
    falsifies_if: not rights_non_derogable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.rights_non_derogable
    proof = ProofObject(
        rule="check_rights_non_derogable",
        premises=[
            "domain=Political Philosophy",
            f"rights_non_derogable={{data.rights_non_derogable}}",
        ],
        conclusion=(
            "PASS: Fundamental rights are non-derogable"
            if success else "FAIL: Fundamental rights are non-derogable"
        ),
    )
    return success, proof


def check_distributive_justice_symmetric(data: PoliticalPhilosophyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Distributive justice principle is symmetric.

    Standard: Political Philosophy domain invariant.
    Falsifies if: not distributive_justice_symmetric.
    falsifies_if: not distributive_justice_symmetric.

    Returns:
        Tuple of (success, proof).
    """
    success = data.distributive_justice_symmetric
    proof = ProofObject(
        rule="check_distributive_justice_symmetric",
        premises=[
            "domain=Political Philosophy",
            f"distributive_justice_symmetric={{data.distributive_justice_symmetric}}",
        ],
        conclusion=(
            "PASS: Distributive justice principle is symmetric"
            if success else "FAIL: Distributive justice principle is symmetric"
        ),
    )
    return success, proof


def check_sovereignty_indivisible(data: PoliticalPhilosophyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Sovereignty is indivisible.

    Standard: Political Philosophy domain invariant.
    Falsifies if: not sovereignty_indivisible.
    falsifies_if: not sovereignty_indivisible.

    Returns:
        Tuple of (success, proof).
    """
    success = data.sovereignty_indivisible
    proof = ProofObject(
        rule="check_sovereignty_indivisible",
        premises=[
            "domain=Political Philosophy",
            f"sovereignty_indivisible={{data.sovereignty_indivisible}}",
        ],
        conclusion=(
            "PASS: Sovereignty is indivisible"
            if success else "FAIL: Sovereignty is indivisible"
        ),
    )
    return success, proof


def check_legitimacy_score_fraction(data: PoliticalPhilosophyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Legitimacy score is between 0 and 1.

    Standard: Political Philosophy domain invariant.
    Falsifies if: not legitimacy_score.
    falsifies_if: not legitimacy_score.

    Returns:
        Tuple of (success, proof).
    """
    success = data.legitimacy_score >= Fraction(0)
    proof = ProofObject(
        rule="check_legitimacy_score_fraction",
        premises=[
            "domain=Political Philosophy",
            f"legitimacy_score={{data.legitimacy_score}}",
        ],
        conclusion=(
            "PASS: Legitimacy score is between 0 and 1 is non-negative"
            if success else "FAIL: Legitimacy score is between 0 and 1 is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Political Philosophy nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_social_contract_consensual", check_social_contract_consensual),
        ("check_rights_non_derogable", check_rights_non_derogable),
        ("check_distributive_justice_symmetric", check_distributive_justice_symmetric),
        ("check_sovereignty_indivisible", check_sovereignty_indivisible),
        ("check_legitimacy_score_fraction", check_legitimacy_score_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
