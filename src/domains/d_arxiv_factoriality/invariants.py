"""Invariant checks for d_arxiv_factoriality."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import FactorialityClaim, create_nominal_claim


def check_ufd_property(data: FactorialityClaim) -> Tuple[bool, ProofObject]:
    """Ring must have unique factorization domain property.

    Standard: arXiv 2604.05238v1 (cs.LO) claim operationalization.
    Falsifies if: not is_ufd.
    falsifies_if: not is_ufd.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_ufd
    proof = ProofObject(
        rule="check_ufd_property",
        premises=["paper_id=2604.05238v1", f"is_ufd={data.is_ufd}"],
        conclusion=(
            "PASS: ring is a UFD"
            if success
            else "FAIL: ring is not a UFD"
        ),
    )
    return success, proof


def check_noetherian_property(data: FactorialityClaim) -> Tuple[bool, ProofObject]:
    """Ring must satisfy ascending chain condition.

    Standard: arXiv 2604.05238v1 (cs.LO) claim operationalization.
    Falsifies if: not is_noetherian.
    falsifies_if: not is_noetherian.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_noetherian
    proof = ProofObject(
        rule="check_noetherian_property",
        premises=["paper_id=2604.05238v1", f"is_noetherian={data.is_noetherian}"],
        conclusion=(
            "PASS: ring is Noetherian"
            if success
            else "FAIL: ring is not Noetherian"
        ),
    )
    return success, proof


def check_localization_ufd(data: FactorialityClaim) -> Tuple[bool, ProofObject]:
    """Localization at primes must be UFD.

    Standard: arXiv 2604.05238v1 (cs.LO) claim operationalization.
    Falsifies if: not localization_is_ufd.
    falsifies_if: not localization_is_ufd.

    Returns:
        Tuple of (success, proof).
    """
    success = data.localization_is_ufd
    proof = ProofObject(
        rule="check_localization_ufd",
        premises=["paper_id=2604.05238v1", f"localization_is_ufd={data.localization_is_ufd}"],
        conclusion=(
            "PASS: localization is UFD"
            if success
            else "FAIL: localization is not UFD"
        ),
    )
    return success, proof


def check_prime_generators_positive(data: FactorialityClaim) -> Tuple[bool, ProofObject]:
    """Ring must have at least one prime generator.

    Standard: arXiv 2604.05238v1 (cs.LO) claim operationalization.
    Falsifies if: prime_generator_count < 1.
    falsifies_if: prime_generator_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.prime_generator_count >= Fraction(1)
    proof = ProofObject(
        rule="check_prime_generators_positive",
        premises=["paper_id=2604.05238v1", f"prime_generator_count={data.prime_generator_count}"],
        conclusion=(
            "PASS: prime generator count is positive"
            if success
            else "FAIL: prime generator count is zero or negative"
        ),
    )
    return success, proof


def check_nagata_criterion(data: FactorialityClaim) -> Tuple[bool, ProofObject]:
    """Nagata criterion: prime generators + Noetherian + localization UFD implies UFD.

    Standard: arXiv 2604.05238v1 (cs.LO) claim operationalization.
    Falsifies if: prime_generator_count >= 1 and is_noetherian and localization_is_ufd and not is_ufd.
    falsifies_if: prime_generator_count >= 1 and is_noetherian and localization_is_ufd and not is_ufd.

    Returns:
        Tuple of (success, proof).
    """
    antecedent = (
        data.prime_generator_count >= Fraction(1)
        and data.is_noetherian
        and data.localization_is_ufd
    )
    success = not antecedent or data.is_ufd
    proof = ProofObject(
        rule="check_nagata_criterion",
        premises=[
            "paper_id=2604.05238v1",
            f"prime_generator_count={data.prime_generator_count}",
            f"is_noetherian={data.is_noetherian}",
            f"localization_is_ufd={data.localization_is_ufd}",
            f"is_ufd={data.is_ufd}",
        ],
        conclusion=(
            "PASS: Nagata criterion satisfied"
            if success
            else "FAIL: Nagata criterion violated"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.05238v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_ufd_property", check_ufd_property),
        ("check_noetherian_property", check_noetherian_property),
        ("check_localization_ufd", check_localization_ufd),
        ("check_prime_generators_positive", check_prime_generators_positive),
        ("check_nagata_criterion", check_nagata_criterion),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
