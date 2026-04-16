"""Invariant checks for d_arxiv_safeadapt_provably_safe."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import SafeAdaptPolicyUpdateClaim, create_nominal_claim


def check_safety_constraint_preservation(data: SafeAdaptPolicyUpdateClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Policy update should preserve or improve safety-constraint satisfaction.

    Standard: arXiv 2604.09452v1 (cs.AI) claim operationalization.
    falsifies_if: safety_constraint_satisfaction_after < safety_constraint_satisfaction_before.

    Returns:
        Tuple of (success, proof).
    """
    success = data.safety_constraint_satisfaction_after >= data.safety_constraint_satisfaction_before
    proof = ProofObject(
        rule="check_safety_constraint_preservation",
        premises=[
            "paper_id=2604.09452v1",
            f"safety_constraint_satisfaction_before={data.safety_constraint_satisfaction_before}",
            f"safety_constraint_satisfaction_after={data.safety_constraint_satisfaction_after}",
        ],
        conclusion=(
            "PASS: safety constraints are preserved during adaptation"
            if success else "FAIL: safety constraint satisfaction regressed"
        ),
    )
    return success, proof

def check_violation_probability_cap(data: SafeAdaptPolicyUpdateClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Constraint violation probability should stay below certified cap.

    Standard: arXiv 2604.09452v1 (cs.AI) claim operationalization.
    falsifies_if: constraint_violation_probability > 1/20.

    Returns:
        Tuple of (success, proof).
    """
    success = data.constraint_violation_probability <= Fraction(1, 20)
    proof = ProofObject(
        rule="check_violation_probability_cap",
        premises=[
            "paper_id=2604.09452v1",
            f"constraint_violation_probability={data.constraint_violation_probability}",
            f"formal_safety_margin={data.formal_safety_margin}",
        ],
        conclusion=(
            "PASS: violation probability is within certified cap"
            if success else "FAIL: violation probability exceeds certified cap"
        ),
    )
    return success, proof

def check_return_non_degradation(data: SafeAdaptPolicyUpdateClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Safe policy update should not degrade task return.

    Standard: arXiv 2604.09452v1 (cs.AI) claim operationalization.
    falsifies_if: task_return_after < task_return_before.

    Returns:
        Tuple of (success, proof).
    """
    success = data.task_return_after >= data.task_return_before
    proof = ProofObject(
        rule="check_return_non_degradation",
        premises=[
            "paper_id=2604.09452v1",
            f"task_return_before={data.task_return_before}",
            f"task_return_after={data.task_return_after}",
        ],
        conclusion=(
            "PASS: task return is preserved or improved"
            if success else "FAIL: task return degraded after safe update"
        ),
    )
    return success, proof

def check_formal_margin_positive(data: SafeAdaptPolicyUpdateClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Provable update guarantee requires positive formal safety margin.

    Standard: arXiv 2604.09452v1 (cs.AI) claim operationalization.
    falsifies_if: formal_safety_margin <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.formal_safety_margin > Fraction(0)
    proof = ProofObject(
        rule="check_formal_margin_positive",
        premises=[
            "paper_id=2604.09452v1",
            f"formal_safety_margin={data.formal_safety_margin}",
            f"adaptation_step_count={data.adaptation_step_count}",
        ],
        conclusion=(
            "PASS: formal safety margin remains positive"
            if success else "FAIL: formal safety margin is non-positive"
        ),
    )
    return success, proof

def check_shift_resilience_floor(data: SafeAdaptPolicyUpdateClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Adapted policy should retain resilience under non-stationary dynamics.

    Standard: arXiv 2604.09452v1 (cs.AI) claim operationalization.
    falsifies_if: distribution_shift_resilience < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.distribution_shift_resilience >= Fraction(3, 4)
    proof = ProofObject(
        rule="check_shift_resilience_floor",
        premises=[
            "paper_id=2604.09452v1",
            f"distribution_shift_resilience={data.distribution_shift_resilience}",
            f"adaptation_step_count={data.adaptation_step_count}",
        ],
        conclusion=(
            "PASS: policy remains resilient under distribution shift"
            if success else "FAIL: resilience under distribution shift is insufficient"
        ),
    )
    return success, proof

def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09452v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_safety_constraint_preservation", check_safety_constraint_preservation),
        ("check_violation_probability_cap", check_violation_probability_cap),
        ("check_return_non_degradation", check_return_non_degradation),
        ("check_formal_margin_positive", check_formal_margin_positive),
        ("check_shift_resilience_floor", check_shift_resilience_floor),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
