#!/usr/bin/env python3
"""Game Theory Invariants — Nash, zero-sum, Pareto."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import NashSolver, ZeroSumVerifier, ParetoFrontier


def check_nash_equilibrium(solver: NashSolver) -> Tuple[bool, ProofObject]:
    """Verify strategy profile is Nash equilibrium.

    Falsifies if: a profitable unilateral deviation exists.
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
