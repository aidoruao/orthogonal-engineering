"""Invariant checks for d_arxiv_imprecise_probability."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import ImpreciseProbabilityClaim, create_nominal_claim


def check_credal_interval_validity(data: ImpreciseProbabilityClaim) -> Tuple[bool, ProofObject]:
    """Credal interval must be valid: lower <= upper, both in [0,1].

    Standard: arXiv 2604.09272v1 (cs.LO) claim operationalization.
    Falsifies if: lower > upper or either outside [0,1].
    falsifies_if: lower > upper or either outside [0,1].

    Returns:
        Tuple of (success, proof).
    """
    success = (
        data.lower_probability <= data.upper_probability
        and Fraction(0) <= data.lower_probability
        and data.upper_probability <= Fraction(1)
    )
    proof = ProofObject(
        rule="check_credal_interval_validity",
        premises=[
            "paper_id=2604.09272v1",
            f"lower_probability={data.lower_probability}",
            f"upper_probability={data.upper_probability}",
        ],
        conclusion=(
            "PASS: credal interval is valid"
            if success
            else "FAIL: credal interval invalid"
        ),
    )
    return success, proof


def check_credal_set_nonempty(data: ImpreciseProbabilityClaim) -> Tuple[bool, ProofObject]:
    """Credal set must be non-empty (size >= 1).

    Standard: arXiv 2604.09272v1 (cs.LO) claim operationalization.
    Falsifies if: credal_set_size < 1.
    falsifies_if: credal_set_size < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.credal_set_size >= Fraction(1)
    proof = ProofObject(
        rule="check_credal_set_nonempty",
        premises=["paper_id=2604.09272v1", f"credal_set_size={data.credal_set_size}"],
        conclusion=(
            "PASS: credal set is non-empty"
            if success
            else "FAIL: credal set is empty"
        ),
    )
    return success, proof


def check_scott_continuity(data: ImpreciseProbabilityClaim) -> Tuple[bool, ProofObject]:
    """Valuation must be Scott-continuous.

    Standard: arXiv 2604.09272v1 (cs.LO) claim operationalization.
    Falsifies if: not is_scott_continuous.
    falsifies_if: not is_scott_continuous.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_scott_continuous
    proof = ProofObject(
        rule="check_scott_continuity",
        premises=["paper_id=2604.09272v1", f"is_scott_continuous={data.is_scott_continuous}"],
        conclusion=(
            "PASS: valuation is Scott-continuous"
            if success
            else "FAIL: valuation is not Scott-continuous"
        ),
    )
    return success, proof


def check_domain_theoretic_bound(data: ImpreciseProbabilityClaim) -> Tuple[bool, ProofObject]:
    """Upper minus lower probability must be at most 1.

    Standard: arXiv 2604.09272v1 (cs.LO) claim operationalization.
    Falsifies if: upper - lower > 1.
    falsifies_if: upper - lower > 1.

    Returns:
        Tuple of (success, proof).
    """
    gap = data.upper_probability - data.lower_probability
    success = gap <= Fraction(1)
    proof = ProofObject(
        rule="check_domain_theoretic_bound",
        premises=["paper_id=2604.09272v1", f"gap={gap}"],
        conclusion=(
            "PASS: domain-theoretic bound satisfied"
            if success
            else "FAIL: domain-theoretic bound violated"
        ),
    )
    return success, proof


def check_vacuous_coherence(data: ImpreciseProbabilityClaim) -> Tuple[bool, ProofObject]:
    """Vacuous credal set (lower=0, upper=1) must still be non-empty.

    Standard: arXiv 2604.09272v1 (cs.LO) claim operationalization.
    Falsifies if: lower == 0 and upper == 1 and credal_set_size < 1.
    falsifies_if: lower == 0 and upper == 1 and credal_set_size < 1.

    Returns:
        Tuple of (success, proof).
    """
    is_vacuous = (
        data.lower_probability == Fraction(0)
        and data.upper_probability == Fraction(1)
    )
    success = not is_vacuous or data.credal_set_size >= Fraction(1)
    proof = ProofObject(
        rule="check_vacuous_coherence",
        premises=[
            "paper_id=2604.09272v1",
            f"is_vacuous={is_vacuous}",
            f"credal_set_size={data.credal_set_size}",
        ],
        conclusion=(
            "PASS: vacuous coherence holds"
            if success
            else "FAIL: vacuous coherence violated"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.09272v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_credal_interval_validity", check_credal_interval_validity),
        ("check_credal_set_nonempty", check_credal_set_nonempty),
        ("check_scott_continuity", check_scott_continuity),
        ("check_domain_theoretic_bound", check_domain_theoretic_bound),
        ("check_vacuous_coherence", check_vacuous_coherence),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
