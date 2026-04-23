#!/usr/bin/env python3
"""D_ARC_AGI Invariants — ARC-AGI Excedent

Verifies nonzero solve rate, compositional depth, novel rule generalization,
exact grid match, no brute force, and cross-task transfer.
"""

from fractions import Fraction
from typing import Tuple, Dict
from axioms.logic import ProofObject
from .implementation import ARCTask, ARCScore


def check_solve_rate_nonzero(score: ARCScore) -> Tuple[bool, ProofObject]:
    """
    ARC-AGI solve rate must exceed zero.

    Standard: ARC-AGI-3 — solve_rate > Fraction(0, 1) (beat current 0%)
    Falsifies if: solve_rate == Fraction(0, 1)
    falsifies_if: solve_rate == Fraction(0, 1)
    """
    if score.solve_rate == Fraction(0, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: solve_rate is zero",
            premises=[
                f"Model: {score.model_id}",
                f"Solve rate: {score.solve_rate}",
            ],
            rule="solve_rate_nonzero",
        )
    return True, ProofObject(
        conclusion=f"solve_rate {score.solve_rate} nonzero",
        premises=[f"Solve rate: {score.solve_rate}"],
        rule="solve_rate_nonzero",
    )


def check_compositional_depth(score: ARCScore) -> Tuple[bool, ProofObject]:
    """
    Compositional generalization must reach depth >= 3.

    Standard: Compositional generalization — compositional_max_depth >= 3
    Falsifies if: compositional_max_depth < 3
    falsifies_if: compositional_max_depth < 3
    """
    if score.compositional_max_depth < 3:
        return False, ProofObject(
            conclusion=f"VIOLATION: compositional_max_depth {score.compositional_max_depth} < 3",
            premises=[
                f"Model: {score.model_id}",
                f"Max depth: {score.compositional_max_depth}",
            ],
            rule="compositional_depth",
        )
    return True, ProofObject(
        conclusion=f"compositional_max_depth {score.compositional_max_depth} >= 3",
        premises=[f"Max depth: {score.compositional_max_depth}"],
        rule="compositional_depth",
    )


def check_novel_rule_generalization(score: ARCScore) -> Tuple[bool, ProofObject]:
    """
    Novel rule transfer rate must exceed 50%.

    Standard: Novel rule transfer — novel_rule_rate > Fraction(1, 2)
    Falsifies if: novel_rule_rate <= Fraction(1, 2)
    falsifies_if: novel_rule_rate <= Fraction(1, 2)
    """
    threshold = Fraction(1, 2)
    if score.novel_rule_rate <= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: novel_rule_rate {score.novel_rule_rate} <= {threshold}",
            premises=[
                f"Model: {score.model_id}",
                f"Novel rule rate: {score.novel_rule_rate}",
                f"Threshold: {threshold}",
            ],
            rule="novel_rule_generalization",
        )
    return True, ProofObject(
        conclusion=f"novel_rule_rate {score.novel_rule_rate} exceeds {threshold}",
        premises=[f"Novel rule rate: {score.novel_rule_rate}", f"Threshold: {threshold}"],
        rule="novel_rule_generalization",
    )


def check_grid_output_exact(task: ARCTask, predicted: Tuple[Tuple[int, ...], ...]) -> Tuple[bool, ProofObject]:
    """
    Predicted grid must exactly match the task output grid.

    Standard: Exact match — predicted == task.output_grid
    Falsifies if: predicted != task.output_grid
    falsifies_if: predicted != task.output_grid
    """
    if predicted != task.output_grid:
        return False, ProofObject(
            conclusion=f"VIOLATION: predicted grid does not match task {task.task_id}",
            premises=[
                f"Task: {task.task_id}",
                f"Expected: {task.output_grid}",
                f"Predicted: {predicted}",
            ],
            rule="grid_output_exact",
        )
    return True, ProofObject(
        conclusion=f"Predicted grid matches task {task.task_id}",
        premises=[f"Task: {task.task_id}"],
        rule="grid_output_exact",
    )


def check_no_brute_force(score: ARCScore, solution_method: str) -> Tuple[bool, ProofObject]:
    """
    Solutions must use rule inference, not brute force.

    Standard: Rule inference required — solution_method != "brute_force"
    Falsifies if: solution_method == "brute_force"
    falsifies_if: solution_method == "brute_force"
    """
    if solution_method == "brute_force":
        return False, ProofObject(
            conclusion=f"VIOLATION: solution method is brute_force for model {score.model_id}",
            premises=[
                f"Model: {score.model_id}",
                f"Solution method: {solution_method}",
            ],
            rule="no_brute_force",
        )
    return True, ProofObject(
        conclusion=f"Solution method '{solution_method}' valid for model {score.model_id}",
        premises=[f"Solution method: {solution_method}"],
        rule="no_brute_force",
    )


def check_transfer_across_tasks(transfer_rate: Fraction) -> Tuple[bool, ProofObject]:
    """
    Cross-task transfer rate must be at least 25%.

    Standard: Cross-task transfer — transfer_rate >= Fraction(1, 4)
    Falsifies if: transfer_rate < Fraction(1, 4)
    falsifies_if: transfer_rate < Fraction(1, 4)
    """
    threshold = Fraction(1, 4)
    if transfer_rate < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: transfer_rate {transfer_rate} < {threshold}",
            premises=[
                f"Transfer rate: {transfer_rate}",
                f"Threshold: {threshold}",
            ],
            rule="transfer_across_tasks",
        )
    return True, ProofObject(
        conclusion=f"transfer_rate {transfer_rate} meets {threshold}",
        premises=[f"Transfer rate: {transfer_rate}", f"Threshold: {threshold}"],
        rule="transfer_across_tasks",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_ARC_AGI invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing data
    passing_task = ARCTask(
        task_id="arc_001",
        input_grid=((0, 0), (0, 1)),
        output_grid=((1, 1), (1, 0)),
        rule_description="invert",
        compositional_depth=3,
    )
    passing_score = ARCScore(
        model_id="oe-arc-solver",
        tasks_solved=5,
        tasks_total=100,
        solve_rate=Fraction(5, 100),
        compositional_max_depth=4,
        novel_rule_rate=Fraction(60, 100),
    )

    # Failing data
    failing_task = ARCTask(
        task_id="arc_002",
        input_grid=((0, 0), (0, 1)),
        output_grid=((1, 1), (1, 0)),
        rule_description="rotate",
        compositional_depth=2,
    )
    failing_score = ARCScore(
        model_id="baseline-arc",
        tasks_solved=0,
        tasks_total=100,
        solve_rate=Fraction(0, 1),
        compositional_max_depth=2,
        novel_rule_rate=Fraction(40, 100),
    )

    results: Dict[str, str] = {}

    checks = [
        ("check_solve_rate_nonzero", lambda: check_solve_rate_nonzero(passing_score)),
        ("check_solve_rate_nonzero_fail", lambda: check_solve_rate_nonzero(failing_score)),
        ("check_compositional_depth", lambda: check_compositional_depth(passing_score)),
        ("check_compositional_depth_fail", lambda: check_compositional_depth(failing_score)),
        ("check_novel_rule_generalization", lambda: check_novel_rule_generalization(passing_score)),
        ("check_novel_rule_generalization_fail", lambda: check_novel_rule_generalization(failing_score)),
        ("check_grid_output_exact", lambda: check_grid_output_exact(passing_task, ((1, 1), (1, 0)))),
        ("check_grid_output_exact_fail", lambda: check_grid_output_exact(passing_task, ((0, 0), (0, 0)))),
        ("check_no_brute_force", lambda: check_no_brute_force(passing_score, "rule_inference")),
        ("check_no_brute_force_fail", lambda: check_no_brute_force(failing_score, "brute_force")),
        ("check_transfer_across_tasks", lambda: check_transfer_across_tasks(Fraction(30, 100))),
        ("check_transfer_across_tasks_fail", lambda: check_transfer_across_tasks(Fraction(15, 100))),
    ]

    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:  # pragma: no cover
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    results = run_all_invariants()
    for k, v in results.items():
        print(f"{k}: {v}")
    failures = [k for k, v in results.items() if not v.startswith("PASS") and not k.endswith("_fail")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ARC_AGI invariants: PASS")
