#!/usr/bin/env python3
"""D_LIVECODEBENCH Invariants — LiveCodeBench Excedent

Verifies hard-rate excedent, contamination freedom, solution correctness,
time-complexity optimality, and overall excedent.
"""

from fractions import Fraction
from typing import Tuple, List
from axioms.logic import ProofObject
from .implementation import LiveCodeProblem, LiveCodeScore


def check_hard_rate_excedent(score: LiveCodeScore) -> Tuple[bool, ProofObject]:
    """
    Hard problem rate must exceed 83%.

    Standard: Hard problem rate > Fraction(83, 100) (Kimi K2 SOTA)
    falsifies_if: hard_rate <= Fraction(83, 100)
    """
    threshold = Fraction(83, 100)
    if score.hard_rate <= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: hard_rate {score.hard_rate} <= {threshold}",
            premises=[
                f"Model: {score.model_id}",
                f"Hard rate: {score.hard_rate}",
                f"Threshold: {threshold}",
            ],
            rule="hard_rate_excedent",
        )
    return True, ProofObject(
        conclusion=f"hard_rate {score.hard_rate} exceeds {threshold}",
        premises=[f"Hard rate: {score.hard_rate}", f"Threshold: {threshold}"],
        rule="hard_rate_excedent",
    )


def check_contamination_free(score: LiveCodeScore) -> Tuple[bool, ProofObject]:
    """
    Evaluation set must be free of training-data contamination.

    Standard: All problems post-training-cutoff
    falsifies_if: contamination_free == False
    """
    if not score.contamination_free:
        return False, ProofObject(
            conclusion=f"VIOLATION: contamination_free is False",
            premises=[
                f"Model: {score.model_id}",
                f"Contamination free: {score.contamination_free}",
            ],
            rule="contamination_free",
        )
    return True, ProofObject(
        conclusion="Evaluation set contamination-free",
        premises=[f"Contamination free: {score.contamination_free}"],
        rule="contamination_free",
    )


def check_solution_correctness(problem: LiveCodeProblem) -> Tuple[bool, ProofObject]:
    """
    Every solved problem must have a correct solution.

    Standard: Every solved problem must be correct
    falsifies_if: solved AND NOT solution_correct
    """
    if problem.solved and not problem.solution_correct:
        return False, ProofObject(
            conclusion=f"VIOLATION: problem {problem.problem_id} solved but incorrect",
            premises=[
                f"Problem: {problem.problem_id}",
                f"Solved: {problem.solved}",
                f"Solution correct: {problem.solution_correct}",
            ],
            rule="solution_correctness",
        )
    return True, ProofObject(
        conclusion=f"Problem {problem.problem_id} correctness valid",
        premises=[f"Solved: {problem.solved}", f"Solution correct: {problem.solution_correct}"],
        rule="solution_correctness",
    )


def check_time_complexity_optimal(problem: LiveCodeProblem) -> Tuple[bool, ProofObject]:
    """
    Solved problems must use asymptotically optimal solutions.

    Standard: Solutions must be asymptotically optimal
    falsifies_if: solved AND NOT time_complexity_optimal
    """
    if problem.solved and not problem.time_complexity_optimal:
        return False, ProofObject(
            conclusion=f"VIOLATION: problem {problem.problem_id} solved but complexity not optimal",
            premises=[
                f"Problem: {problem.problem_id}",
                f"Solved: {problem.solved}",
                f"Time complexity optimal: {problem.time_complexity_optimal}",
            ],
            rule="time_complexity_optimal",
        )
    return True, ProofObject(
        conclusion=f"Problem {problem.problem_id} complexity optimal",
        premises=[f"Solved: {problem.solved}", f"Time complexity optimal: {problem.time_complexity_optimal}"],
        rule="time_complexity_optimal",
    )


def check_overall_excedent(score: LiveCodeScore) -> Tuple[bool, ProofObject]:
    """
    Overall solve rate must exceed 85%.

    Standard: overall_rate > Fraction(85, 100)
    falsifies_if: overall_rate <= Fraction(85, 100)
    """
    threshold = Fraction(85, 100)
    if score.overall_rate <= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: overall_rate {score.overall_rate} <= {threshold}",
            premises=[
                f"Model: {score.model_id}",
                f"Overall rate: {score.overall_rate}",
                f"Threshold: {threshold}",
            ],
            rule="overall_excedent",
        )
    return True, ProofObject(
        conclusion=f"overall_rate {score.overall_rate} exceeds {threshold}",
        premises=[f"Overall rate: {score.overall_rate}", f"Threshold: {threshold}"],
        rule="overall_excedent",
    )


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all D_LIVECODEBENCH invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing data
    passing_score = LiveCodeScore(
        model_id="kimi-k2-sota",
        easy_rate=Fraction(95, 100),
        medium_rate=Fraction(90, 100),
        hard_rate=Fraction(87, 100),
        overall_rate=Fraction(91, 100),
        contamination_free=True,
    )
    passing_problem = LiveCodeProblem(
        problem_id="lc_001",
        difficulty="hard",
        publication_date="2025-03-01",
        solved=True,
        solution_correct=True,
        time_complexity_optimal=True,
    )

    # Failing data
    failing_score = LiveCodeScore(
        model_id="baseline-model",
        easy_rate=Fraction(80, 100),
        medium_rate=Fraction(75, 100),
        hard_rate=Fraction(80, 100),
        overall_rate=Fraction(82, 100),
        contamination_free=False,
    )
    failing_problem = LiveCodeProblem(
        problem_id="lc_002",
        difficulty="hard",
        publication_date="2024-01-01",
        solved=True,
        solution_correct=False,
        time_complexity_optimal=False,
    )

    results: List[Tuple[str, bool, ProofObject]] = []

    checks = [
        ("check_hard_rate_excedent", lambda: check_hard_rate_excedent(passing_score)),
        ("check_hard_rate_excedent_fail", lambda: check_hard_rate_excedent(failing_score)),
        ("check_contamination_free", lambda: check_contamination_free(passing_score)),
        ("check_contamination_free_fail", lambda: check_contamination_free(failing_score)),
        ("check_solution_correctness", lambda: check_solution_correctness(passing_problem)),
        ("check_solution_correctness_fail", lambda: check_solution_correctness(failing_problem)),
        ("check_time_complexity_optimal", lambda: check_time_complexity_optimal(passing_problem)),
        ("check_time_complexity_optimal_fail", lambda: check_time_complexity_optimal(failing_problem)),
        ("check_overall_excedent", lambda: check_overall_excedent(passing_score)),
        ("check_overall_excedent_fail", lambda: check_overall_excedent(failing_score)),
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
    print("All D_LIVECODEBENCH invariants: PASS")
