#!/usr/bin/env python3
"""Game Theory Invariants — Nash, zero-sum, Pareto.

Nash (1950): 'Equilibrium Points in n-Person Games'.
von Neumann & Morgenstern (1944): Theory of Games and Economic Behavior.
Pareto (1906): Manual of Political Economy.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Game,
    NashSolver,
    ParetoFrontier,
    ZeroSumVerifier,
)


def check_nash_equilibrium(solver: NashSolver) -> Tuple[bool, ProofObject]:
    """Verify strategy profile is Nash equilibrium.

    Falsifies if: nash_stability_score < Fraction(1, 1).
    falsifies_if: nash_stability_score < Fraction(1, 1).
    """
    score = solver.nash_stability_score()
    deviations = solver.deviation_count()
    if score < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Not a Nash equilibrium — stability score {score}, {deviations} profitable deviation(s)",
            premises=[
                f"Profile: {solver.equilibrium_profile}",
                f"Stability score: {score}",
                f"Profitable deviations: {deviations}",
            ],
            rule="nash_equilibrium"
        )
    return True, ProofObject(
        conclusion=f"Nash equilibrium verified — stability score {score}",
        premises=[f"Profile: {solver.equilibrium_profile}", f"Score: {score}"],
        rule="nash_equilibrium"
    )


def check_zero_sum_property(verifier: ZeroSumVerifier) -> Tuple[bool, ProofObject]:
    """Zero-sum game: payoffs sum to zero for all profiles.

    Falsifies if: zero_sum_deviation > Fraction(0, 1).
    falsifies_if: zero_sum_deviation > Fraction(0, 1).
    """
    deviation = verifier.zero_sum_deviation()
    if deviation > Fraction(0, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Game not zero-sum — deviation {deviation}",
            premises=[
                f"Max absolute sum: {deviation}",
                f"Expected: 0",
            ],
            rule="zero_sum_property"
        )
    return True, ProofObject(
        conclusion=f"Zero-sum property satisfied — deviation {deviation}",
        premises=[f"Deviation: {deviation}"],
        rule="zero_sum_property"
    )


def check_pareto_optimality(frontier: ParetoFrontier, outcome: Tuple[str, ...]) -> Tuple[bool, ProofObject]:
    """Verify outcome is Pareto optimal.

    Falsifies if: improvement_margin > Fraction(0, 1).
    falsifies_if: improvement_margin > Fraction(0, 1).
    """
    margin = frontier.improvement_margin(outcome)
    ratio = frontier.pareto_efficiency_ratio()
    if margin > Fraction(0, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Outcome not Pareto optimal — improvement margin {margin}",
            premises=[
                f"Outcome: {outcome}",
                f"Improvement margin: {margin}",
                f"Efficiency ratio: {ratio}",
            ],
            rule="pareto_optimality"
        )
    return True, ProofObject(
        conclusion=f"Pareto optimality confirmed — margin {margin}",
        premises=[f"Outcome: {outcome}", f"Margin: {margin}", f"Efficiency ratio: {ratio}"],
        rule="pareto_optimality"
    )


def run_all_invariants() -> dict:
    """Run all D_GAME_THEORY invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing: Prisoner's Dilemma equilibrium (both defect)
    pass_game = Game(
        players=["A", "B"],
        strategies={"A": ["Cooperate", "Defect"], "B": ["Cooperate", "Defect"]},
        payoffs={
            ("Cooperate", "Cooperate"): [Fraction(3), Fraction(3)],
            ("Cooperate", "Defect"): [Fraction(0), Fraction(5)],
            ("Defect", "Cooperate"): [Fraction(5), Fraction(0)],
            ("Defect", "Defect"): [Fraction(1), Fraction(1)],
        },
    )
    pass_nash = NashSolver(
        game=pass_game,
        equilibrium_profile=("Defect", "Defect"),
    )
    pass_zero = ZeroSumVerifier(
        game=Game(
            players=["A", "B"],
            strategies={"A": ["Up", "Down"], "B": ["Left", "Right"]},
            payoffs={
                ("Up", "Left"): [Fraction(1), Fraction(-1)],
                ("Up", "Right"): [Fraction(-1), Fraction(1)],
                ("Down", "Left"): [Fraction(-1), Fraction(1)],
                ("Down", "Right"): [Fraction(1), Fraction(-1)],
            },
        ),
    )
    pass_pareto = ParetoFrontier(
        outcomes=[("Cooperate", "Cooperate"), ("Defect", "Defect")],
        payoffs={
            ("Cooperate", "Cooperate"): [Fraction(3), Fraction(3)],
            ("Defect", "Defect"): [Fraction(1), Fraction(1)],
        },
    )

    # Failing: Cooperate is NOT Nash equilibrium in PD
    fail_nash = NashSolver(
        game=pass_game,
        equilibrium_profile=("Cooperate", "Cooperate"),
    )
    fail_zero = ZeroSumVerifier(
        game=Game(
            players=["A", "B"],
            strategies={"A": ["Up", "Down"], "B": ["Left", "Right"]},
            payoffs={
                ("Up", "Left"): [Fraction(1), Fraction(0)],
                ("Up", "Right"): [Fraction(0), Fraction(1)],
                ("Down", "Left"): [Fraction(0), Fraction(1)],
                ("Down", "Right"): [Fraction(1), Fraction(0)],
            },
        ),
    )
    fail_pareto = ParetoFrontier(
        outcomes=[("Cooperate", "Cooperate"), ("Defect", "Defect")],
        payoffs={
            ("Cooperate", "Cooperate"): [Fraction(3), Fraction(3)],
            ("Defect", "Defect"): [Fraction(4), Fraction(4)],
        },
    )

    checks = [
        ("check_nash_equilibrium_pass", lambda: check_nash_equilibrium(pass_nash)),
        ("check_nash_equilibrium_fail", lambda: check_nash_equilibrium(fail_nash)),
        ("check_zero_sum_property_pass", lambda: check_zero_sum_property(pass_zero)),
        ("check_zero_sum_property_fail", lambda: check_zero_sum_property(fail_zero)),
        ("check_pareto_optimality_pass", lambda: check_pareto_optimality(pass_pareto, ("Cooperate", "Cooperate"))),
        ("check_pareto_optimality_fail", lambda: check_pareto_optimality(fail_pareto, ("Cooperate", "Cooperate"))),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS") and not k.endswith("_fail")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_GAME_THEORY invariants: PASS")
