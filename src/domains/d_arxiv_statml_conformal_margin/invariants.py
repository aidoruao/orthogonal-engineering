"""Invariant checks for d_arxiv_statml_conformal_margin."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ConformalMarginClaim, create_nominal_claim


def check_margin_positive(data: ConformalMarginClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Classification margin is positive.

    Standard: arXiv 2604.06468v2 (stat.ML) claim operationalization.
    Falsifies if: margin <= 0.
    falsifies_if: margin <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.margin > Fraction(0)
    proof = ProofObject(
        rule="check_margin_positive",
        premises=[
            f"paper_id=2604.06468v2",
            f'margin={data.margin}',
        ],
        conclusion=(
            "PASS: classification margin is positive"
            if success else "FAIL: margin <= 0"
        ),
    )
    return success, proof



def check_noise_rate_valid(data: ConformalMarginClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Label noise rate is in [0, 1/2).

    Standard: arXiv 2604.06468v2 (stat.ML) claim operationalization.
    Falsifies if: noise_rate < 0 or noise_rate >= Fraction(1, 2).
    falsifies_if: noise_rate < 0 or noise_rate >= Fraction(1, 2).

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.noise_rate < Fraction(1, 2)
    proof = ProofObject(
        rule="check_noise_rate_valid",
        premises=[
            f"paper_id=2604.06468v2",
            f'noise_rate={data.noise_rate}',
        ],
        conclusion=(
            "PASS: label noise rate is in [0, 1/2)"
            if success else "FAIL: noise_rate < 0 or noise_rate >= Fraction(1, 2)"
        ),
    )
    return success, proof



def check_coverage_valid(data: ConformalMarginClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Conformal coverage guarantee is in (0, 1].

    Standard: arXiv 2604.06468v2 (stat.ML) claim operationalization.
    Falsifies if: coverage_guarantee <= 0 or coverage_guarantee > 1.
    falsifies_if: coverage_guarantee <= 0 or coverage_guarantee > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.coverage_guarantee <= Fraction(1)
    proof = ProofObject(
        rule="check_coverage_valid",
        premises=[
            f"paper_id=2604.06468v2",
            f'coverage_guarantee={data.coverage_guarantee}',
        ],
        conclusion=(
            "PASS: conformal coverage guarantee is in (0, 1]"
            if success else "FAIL: coverage_guarantee <= 0 or coverage_guarantee > 1"
        ),
    )
    return success, proof



def check_robustness(data: ConformalMarginClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Model is robust to label noise.

    Standard: arXiv 2604.06468v2 (stat.ML) claim operationalization.
    Falsifies if: not is_robust.
    falsifies_if: not is_robust.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_robust is True
    proof = ProofObject(
        rule="check_robustness",
        premises=[
            f"paper_id=2604.06468v2",
            f'is_robust={data.is_robust}',
        ],
        conclusion=(
            "PASS: model is robust to label noise"
            if success else "FAIL: not is_robust"
        ),
    )
    return success, proof



def check_risk_bound_valid(data: ConformalMarginClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Generalization risk bound is in [0, 1].

    Standard: arXiv 2604.06468v2 (stat.ML) claim operationalization.
    Falsifies if: risk_bound < 0 or risk_bound > 1.
    falsifies_if: risk_bound < 0 or risk_bound > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.risk_bound <= Fraction(1)
    proof = ProofObject(
        rule="check_risk_bound_valid",
        premises=[
            f"paper_id=2604.06468v2",
            f'risk_bound={data.risk_bound}',
        ],
        conclusion=(
            "PASS: generalization risk bound is in [0, 1]"
            if success else "FAIL: risk_bound < 0 or risk_bound > 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.06468v2 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_margin_positive", check_margin_positive),
        ("check_noise_rate_valid", check_noise_rate_valid),
        ("check_coverage_valid", check_coverage_valid),
        ("check_robustness", check_robustness),
        ("check_risk_bound_valid", check_risk_bound_valid),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
