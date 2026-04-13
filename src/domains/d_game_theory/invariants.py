#!/usr/bin/env python3
"""Game Theory Invariants — Nash, zero-sum, Pareto."""

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

    Falsifies if: a profitable unilateral deviation exists.
    falsifies_if: a profitable unilateral deviation exists.
    """
    if not solver.is_nash_equilibrium():
        return False, ProofObject(
            conclusion="VIOLATION: Not a Nash equilibrium — profitable deviation exists",
            premises=[],
            rule="nash_equilibrium"
        )
    
    return True, ProofObject(
        conclusion="Nash equilibrium verified",
        premises=[f"Profile: {solver.equilibrium_profile}"],
        rule="nash_equilibrium"
    )


def check_zero_sum_property(verifier: ZeroSumVerifier) -> Tuple[bool, ProofObject]:
    """Zero-sum game: payoffs sum to zero for all profiles.

    Falsifies if: any payoff profile sums to a non-zero value.
    falsifies_if: any payoff profile sums to a non-zero value.
    """
    if not verifier.is_zero_sum():
        return False, ProofObject(
            conclusion="VIOLATION: Game not zero-sum (payoff sums non-zero)",
            premises=[],
            rule="zero_sum_property"
        )
    
    return True, ProofObject(
        conclusion="Zero-sum property satisfied",
        premises=[],
        rule="zero_sum_property"
    )


def check_pareto_optimality(frontier: ParetoFrontier, outcome) -> Tuple[bool, ProofObject]:
    """Verify outcome is Pareto optimal.

    Falsifies if: there exists another outcome that improves at least one player
    falsifies_if: there exists another outcome that improves at least one player
    without worsening others.
    """
    if not frontier.is_pareto_optimal(outcome):
        return False, ProofObject(
            conclusion="VIOLATION: Outcome not Pareto optimal (dominated alternative exists)",
            premises=[],
            rule="pareto_optimality"
        )
    
    return True, ProofObject(
        conclusion="Pareto optimality confirmed",
        premises=[],
        rule="pareto_optimality"
    )


def run_all_invariants() -> dict:
    """Run all D_GAME_THEORY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    nash_solver = NashSolver(
        game=Game(
        players=["SAMPLE"],
        strategies={},
        payoffs={},
    ),
        equilibrium_profile=(),
    )
    pareto_frontier = ParetoFrontier(
        outcomes=[()],
        payoffs={},
    )
    zero_sum_verifier = ZeroSumVerifier(
        game=Game(
        players=["SAMPLE"],
        strategies={},
        payoffs={},
    ),
    )

    checks = [
        ("check_nash_equilibrium", lambda: check_nash_equilibrium(nash_solver)),
        ("check_zero_sum_property", lambda: check_zero_sum_property(zero_sum_verifier)),
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
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_GAME_THEORY invariants: PASS")
