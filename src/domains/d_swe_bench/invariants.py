#!/usr/bin/env python3
"""D_SWE_BENCH Invariants — SWE-bench Excedent

Verifies resolve rate, false positive bounds, patch minimality,
test pass completeness, data leakage absence, and deterministic resolution.
"""

from fractions import Fraction
from typing import Tuple, List
from axioms.logic import ProofObject
from .implementation import SWEBenchInstance, SWEBenchScore


# Simulated training-set registry for leakage detection.
_TRAINING_INSTANCES = {
    ("django", "12345"),
    ("scikit-learn", "67890"),
}


def check_resolve_rate_excedent(score: SWEBenchScore) -> Tuple[bool, ProofObject]:
    """
    SWE-bench Verified resolve rate must exceed 85%.

    Standard: SWE-bench Verified — resolve_rate > Fraction(85, 100)
    falsifies_if: resolve_rate < Fraction(85, 100)
    """
    threshold = Fraction(85, 100)
    if score.resolve_rate < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: resolve_rate {score.resolve_rate} < {threshold}",
            premises=[
                f"Model: {score.model_id}",
                f"Split: {score.split}",
                f"Resolve rate: {score.resolve_rate}",
                f"Threshold: {threshold}",
            ],
            rule="resolve_rate_excedent",
        )
    return True, ProofObject(
        conclusion=f"resolve_rate {score.resolve_rate} exceeds {threshold}",
        premises=[f"Resolve rate: {score.resolve_rate}", f"Threshold: {threshold}"],
        rule="resolve_rate_excedent",
    )


def check_false_positive_bounded(score: SWEBenchScore) -> Tuple[bool, ProofObject]:
    """
    Patch correctness false positive rate must stay below 5%.

    Standard: Patch correctness — false_positive_rate < Fraction(5, 100)
    falsifies_if: false_positive_rate >= Fraction(5, 100)
    """
    threshold = Fraction(5, 100)
    if score.false_positive_rate >= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: false_positive_rate {score.false_positive_rate} >= {threshold}",
            premises=[
                f"Model: {score.model_id}",
                f"False positive rate: {score.false_positive_rate}",
                f"Threshold: {threshold}",
            ],
            rule="false_positive_bounded",
        )
    return True, ProofObject(
        conclusion=f"false_positive_rate {score.false_positive_rate} below {threshold}",
        premises=[f"False positive rate: {score.false_positive_rate}", f"Threshold: {threshold}"],
        rule="false_positive_bounded",
    )


def check_patch_minimality(score: SWEBenchScore) -> Tuple[bool, ProofObject]:
    """
    Average patch size must remain under 50 lines.

    Standard: Minimal diff — avg_patch_size < Fraction(50, 1) lines
    falsifies_if: avg_patch_size >= Fraction(50, 1)
    """
    threshold = Fraction(50, 1)
    if score.avg_patch_size >= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: avg_patch_size {score.avg_patch_size} >= {threshold}",
            premises=[
                f"Model: {score.model_id}",
                f"Average patch size: {score.avg_patch_size}",
                f"Threshold: {threshold}",
            ],
            rule="patch_minimality",
        )
    return True, ProofObject(
        conclusion=f"avg_patch_size {score.avg_patch_size} under {threshold}",
        premises=[f"Average patch size: {score.avg_patch_size}", f"Threshold: {threshold}"],
        rule="patch_minimality",
    )


def check_test_pass_completeness(instance: SWEBenchInstance) -> Tuple[bool, ProofObject]:
    """
    All tests must pass for a resolved instance.

    Standard: All tests pass — test_pass_rate == Fraction(1, 1)
    falsifies_if: test_pass_rate < Fraction(1, 1)
    """
    if instance.test_pass_rate < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: test_pass_rate {instance.test_pass_rate} < 1",
            premises=[
                f"Repo: {instance.repo_id}",
                f"Issue: {instance.issue_id}",
                f"Test pass rate: {instance.test_pass_rate}",
            ],
            rule="test_pass_completeness",
        )
    return True, ProofObject(
        conclusion=f"test_pass_rate {instance.test_pass_rate} complete",
        premises=[f"Test pass rate: {instance.test_pass_rate}"],
        rule="test_pass_completeness",
    )


def check_no_data_leakage_swe(score: SWEBenchScore, instance: SWEBenchInstance) -> Tuple[bool, ProofObject]:
    """
    Resolved instance must not appear in training data.

    Standard: Instance not in training data
    falsifies_if: instance in training set AND resolved
    """
    instance_key = (instance.repo_id, instance.issue_id)
    in_training = instance_key in _TRAINING_INSTANCES
    resolved = instance.patch_correctness == Fraction(1, 1)

    if in_training and resolved:
        return False, ProofObject(
            conclusion=f"VIOLATION: instance {instance_key} in training set AND resolved",
            premises=[
                f"Instance: {instance_key}",
                f"In training: {in_training}",
                f"Resolved: {resolved}",
            ],
            rule="no_data_leakage_swe",
        )
    return True, ProofObject(
        conclusion=f"No data leakage for instance {instance_key}",
        premises=[f"Instance: {instance_key}", f"In training: {in_training}", f"Resolved: {resolved}"],
        rule="no_data_leakage_swe",
    )


def check_deterministic_resolution(score1: SWEBenchScore, score2: SWEBenchScore) -> Tuple[bool, ProofObject]:
    """
    Same model and split must produce identical resolve rates.

    Standard: Same instance → same patch (determinism)
    falsifies_if: two runs on same instance produce different patches
    """
    if score1.model_id == score2.model_id and score1.split == score2.split:
        if score1.resolve_rate != score2.resolve_rate:
            return False, ProofObject(
                conclusion=f"VIOLATION: deterministic failure — {score1.resolve_rate} != {score2.resolve_rate}",
                premises=[
                    f"Model: {score1.model_id}",
                    f"Split: {score1.split}",
                    f"Run 1 resolve_rate: {score1.resolve_rate}",
                    f"Run 2 resolve_rate: {score2.resolve_rate}",
                ],
                rule="deterministic_resolution",
            )
    return True, ProofObject(
        conclusion=f"Deterministic resolution verified for {score1.model_id}",
        premises=[
            f"Model: {score1.model_id}",
            f"Split: {score1.split}",
            f"Run 1: {score1.resolve_rate}",
            f"Run 2: {score2.resolve_rate}",
        ],
        rule="deterministic_resolution",
    )


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all D_SWE_BENCH invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing data
    passing_score = SWEBenchScore(
        model_id="kimi-k2-sota",
        split="verified",
        instances_resolved=2300,
        instances_total=2500,
        resolve_rate=Fraction(92, 100),
        false_positive_rate=Fraction(2, 100),
        avg_patch_size=Fraction(30, 1),
    )
    passing_instance = SWEBenchInstance(
        repo_id="sympy",
        issue_id="99999",
        patch_correctness=Fraction(1, 1),
        test_pass_rate=Fraction(1, 1),
        files_modified=2,
        lines_changed=15,
        resolution_type="bug_fix",
    )

    # Failing data
    failing_score = SWEBenchScore(
        model_id="baseline-model",
        split="verified",
        instances_resolved=1800,
        instances_total=2500,
        resolve_rate=Fraction(72, 100),
        false_positive_rate=Fraction(8, 100),
        avg_patch_size=Fraction(65, 1),
    )
    failing_instance = SWEBenchInstance(
        repo_id="django",
        issue_id="12345",
        patch_correctness=Fraction(1, 1),
        test_pass_rate=Fraction(95, 100),
        files_modified=3,
        lines_changed=20,
        resolution_type="bug_fix",
    )
    inconsistent_score = SWEBenchScore(
        model_id="baseline-model",
        split="verified",
        instances_resolved=1800,
        instances_total=2500,
        resolve_rate=Fraction(70, 100),
        false_positive_rate=Fraction(8, 100),
        avg_patch_size=Fraction(65, 1),
    )

    results: List[Tuple[str, bool, ProofObject]] = []

    checks = [
        ("check_resolve_rate_excedent", lambda: check_resolve_rate_excedent(passing_score)),
        ("check_resolve_rate_excedent_fail", lambda: check_resolve_rate_excedent(failing_score)),
        ("check_false_positive_bounded", lambda: check_false_positive_bounded(passing_score)),
        ("check_false_positive_bounded_fail", lambda: check_false_positive_bounded(failing_score)),
        ("check_patch_minimality", lambda: check_patch_minimality(passing_score)),
        ("check_patch_minimality_fail", lambda: check_patch_minimality(failing_score)),
        ("check_test_pass_completeness", lambda: check_test_pass_completeness(passing_instance)),
        ("check_test_pass_completeness_fail", lambda: check_test_pass_completeness(failing_instance)),
        ("check_no_data_leakage_swe", lambda: check_no_data_leakage_swe(passing_score, passing_instance)),
        ("check_no_data_leakage_swe_fail", lambda: check_no_data_leakage_swe(failing_score, failing_instance)),
        ("check_deterministic_resolution", lambda: check_deterministic_resolution(passing_score, passing_score)),
        ("check_deterministic_resolution_fail", lambda: check_deterministic_resolution(failing_score, inconsistent_score)),
    ]

    for name, func in checks:
        try:
            ok, proof = func()
            results.append((name, ok, proof))
        except Exception as exc:  # pragma: no cover
            results.append((name, False, ProofObject(
                rule=name,
                premises=[str(exc)],
                conclusion=f"ERROR: {exc}",
            )))

    return results


if __name__ == "__main__":
    results = run_all_invariants()
    for name, ok, proof in results:
        print(f"{name}: {'PASS' if ok else 'FAIL'} — {proof.conclusion}")
    failures = [name for name, ok, _ in results if not ok]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_SWE_BENCH invariants: PASS")
