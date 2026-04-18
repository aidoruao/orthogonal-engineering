"""Invariant checks for d_arxiv_statml_sequential_audit."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import SequentialAuditClaim, create_nominal_claim


def check_risk_limit_valid(data: SequentialAuditClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Risk limit is in (0, 1).

    Standard: arXiv 2604.06116v1 (stat.ML) claim operationalization.
    Falsifies if: risk_limit <= 0 or risk_limit >= 1.
    falsifies_if: risk_limit <= 0 or risk_limit >= 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.risk_limit < Fraction(1)
    proof = ProofObject(
        rule="check_risk_limit_valid",
        premises=[
            f"paper_id=2604.06116v1",
            f'risk_limit={data.risk_limit}',
        ],
        conclusion=(
            "PASS: risk limit is in (0, 1)"
            if success else "FAIL: risk_limit <= 0 or risk_limit >= 1"
        ),
    )
    return success, proof



def check_sample_size_valid(data: SequentialAuditClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Sample size is in [1, population_size].

    Standard: arXiv 2604.06116v1 (stat.ML) claim operationalization.
    Falsifies if: sample_size < 1 or sample_size > population_size.
    falsifies_if: sample_size < 1 or sample_size > population_size.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(1) <= data.sample_size <= data.population_size
    proof = ProofObject(
        rule="check_sample_size_valid",
        premises=[
            f"paper_id=2604.06116v1",
            f'sample_size={data.sample_size}',
            f'population_size={data.population_size}',
        ],
        conclusion=(
            "PASS: sample size is in [1, population_size]"
            if success else "FAIL: sample_size < 1 or sample_size > population_size"
        ),
    )
    return success, proof



def check_test_statistic_nonnegative(data: SequentialAuditClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Test statistic is non-negative.

    Standard: arXiv 2604.06116v1 (stat.ML) claim operationalization.
    Falsifies if: test_statistic < 0.
    falsifies_if: test_statistic < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.test_statistic >= Fraction(0)
    proof = ProofObject(
        rule="check_test_statistic_nonnegative",
        premises=[
            f"paper_id=2604.06116v1",
            f'test_statistic={data.test_statistic}',
        ],
        conclusion=(
            "PASS: test statistic is non-negative"
            if success else "FAIL: test_statistic < 0"
        ),
    )
    return success, proof



def check_audit_completion(data: SequentialAuditClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Audit has reached sufficient confidence to conclude.

    Standard: arXiv 2604.06116v1 (stat.ML) claim operationalization.
    Falsifies if: not audit_complete.
    falsifies_if: not audit_complete.

    Returns:
        Tuple of (success, proof).
    """
    success = data.audit_complete is True
    proof = ProofObject(
        rule="check_audit_completion",
        premises=[
            f"paper_id=2604.06116v1",
            f'audit_complete={data.audit_complete}',
        ],
        conclusion=(
            "PASS: audit has reached sufficient confidence to conclude"
            if success else "FAIL: not audit_complete"
        ),
    )
    return success, proof



def check_population_size_positive(data: SequentialAuditClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Population size is >= 1.

    Standard: arXiv 2604.06116v1 (stat.ML) claim operationalization.
    Falsifies if: population_size < 1.
    falsifies_if: population_size < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.population_size >= Fraction(1)
    proof = ProofObject(
        rule="check_population_size_positive",
        premises=[
            f"paper_id=2604.06116v1",
            f'population_size={data.population_size}',
        ],
        conclusion=(
            "PASS: population size is >= 1"
            if success else "FAIL: population_size < 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.06116v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_risk_limit_valid", check_risk_limit_valid),
        ("check_sample_size_valid", check_sample_size_valid),
        ("check_test_statistic_nonnegative", check_test_statistic_nonnegative),
        ("check_audit_completion", check_audit_completion),
        ("check_population_size_positive", check_population_size_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
