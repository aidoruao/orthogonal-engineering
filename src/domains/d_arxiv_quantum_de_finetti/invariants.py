"""Invariant checks for d_arxiv_quantum_de_finetti."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumDeFinettiClaim, create_nominal_claim


def check_exchangeability(data: QuantumDeFinettiClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: is_exchangeable must be True.

    Standard: arXiv 2604.09410v1 (quant-ph) claim operationalization.
    Falsifies if: State is not exchangeable.
    falsifies_if: not is_exchangeable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_exchangeable is True
    proof = ProofObject(
        rule="check_exchangeability",
        premises=[
            "paper_id=2604.09410v1",
            f"is_exchangeable={data.is_exchangeable}",
        ],
        conclusion=(
            "PASS: is_exchangeable is True"
            if success else "FAIL: is_exchangeable is not True"
        ),
    )
    return success, proof


def check_subsystem_count_valid(data: QuantumDeFinettiClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: subsystem_count must satisfy 1 <= subsystem_count <= party_count.

    Standard: arXiv 2604.09410v1 (quant-ph) claim operationalization.
    Falsifies if: Subsystem count is out of valid range.
    falsifies_if: subsystem_count < 1 or subsystem_count > party_count.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(1) <= data.subsystem_count <= data.party_count
    proof = ProofObject(
        rule="check_subsystem_count_valid",
        premises=[
            "paper_id=2604.09410v1",
            f"subsystem_count={data.subsystem_count}",
            f"party_count={data.party_count}",
        ],
        conclusion=(
            "PASS: subsystem_count in [1, party_count]"
            if success else "FAIL: subsystem_count out of valid range"
        ),
    )
    return success, proof


def check_de_finetti_error_nonnegative(data: QuantumDeFinettiClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: de_finetti_error must be nonnegative.

    Standard: arXiv 2604.09410v1 (quant-ph) claim operationalization.
    Falsifies if: De Finetti error is negative.
    falsifies_if: de_finetti_error < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.de_finetti_error >= Fraction(0)
    proof = ProofObject(
        rule="check_de_finetti_error_nonnegative",
        premises=[
            "paper_id=2604.09410v1",
            f"de_finetti_error={data.de_finetti_error}",
        ],
        conclusion=(
            "PASS: de_finetti_error >= 0"
            if success else "FAIL: de_finetti_error is negative"
        ),
    )
    return success, proof


def check_dimension_positive(data: QuantumDeFinettiClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: dimension must be at least 1.

    Standard: arXiv 2604.09410v1 (quant-ph) claim operationalization.
    Falsifies if: Dimension is less than 1.
    falsifies_if: dimension < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.dimension >= Fraction(1)
    proof = ProofObject(
        rule="check_dimension_positive",
        premises=[
            "paper_id=2604.09410v1",
            f"dimension={data.dimension}",
        ],
        conclusion=(
            "PASS: dimension >= 1"
            if success else "FAIL: dimension is less than 1"
        ),
    )
    return success, proof


def check_party_count_positive(data: QuantumDeFinettiClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: party_count must be at least 1.

    Standard: arXiv 2604.09410v1 (quant-ph) claim operationalization.
    Falsifies if: Party count is less than 1.
    falsifies_if: party_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.party_count >= Fraction(1)
    proof = ProofObject(
        rule="check_party_count_positive",
        premises=[
            "paper_id=2604.09410v1",
            f"party_count={data.party_count}",
        ],
        conclusion=(
            "PASS: party_count >= 1"
            if success else "FAIL: party_count is less than 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09410v1 (quant-ph) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_exchangeability", check_exchangeability),
        ("check_subsystem_count_valid", check_subsystem_count_valid),
        ("check_de_finetti_error_nonnegative", check_de_finetti_error_nonnegative),
        ("check_dimension_positive", check_dimension_positive),
        ("check_party_count_positive", check_party_count_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
