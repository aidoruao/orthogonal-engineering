"""arXiv-derived domain invariants for Do We Really Need to Approach the Entire Pareto Front in Many-Objective Bayesian Optimisation?"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class ManyObjectiveParetoFocusClaim:
    """Structured claim parameters derived from arXiv paper 2604.09417v1 (cs.AI)."""

    objective_dimension: Fraction
    hypervolume_ratio: Fraction
    knee_region_coverage: Fraction
    full_front_evaluation_cost: Fraction
    focused_search_cost: Fraction
    decision_useful_solution_ratio: Fraction
    knee_region_regret: Fraction
    sample_efficiency_gain: Fraction


def check_many_objective_regime(data: ManyObjectiveParetoFocusClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Claim applies only in many-objective settings (>3 objectives).

    Standard: arXiv 2604.09417v1 (cs.AI) claim operationalization.
    falsifies_if: objective_dimension <= 3.

    Returns:
        Tuple of (success, proof).
    """
    success = data.objective_dimension > Fraction(3)
    proof = ProofObject(
        rule="check_many_objective_regime",
        premises=[
            "paper_id=2604.09417v1",
            f"objective_dimension={data.objective_dimension}",
        ],
        conclusion=(
            "PASS: optimization setting is many-objective"
            if success else "FAIL: objective dimension is not many-objective"
        ),
    )
    return success, proof

def check_knee_region_priority(data: ManyObjectiveParetoFocusClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Focused methods should cover decision-relevant knee region strongly.

    Standard: arXiv 2604.09417v1 (cs.AI) claim operationalization.
    falsifies_if: knee_region_coverage < 4/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.knee_region_coverage >= Fraction(4, 5)
    proof = ProofObject(
        rule="check_knee_region_priority",
        premises=[
            "paper_id=2604.09417v1",
            f"knee_region_coverage={data.knee_region_coverage}",
            f"decision_useful_solution_ratio={data.decision_useful_solution_ratio}",
        ],
        conclusion=(
            "PASS: knee region coverage is high"
            if success else "FAIL: knee region coverage is insufficient"
        ),
    )
    return success, proof

def check_focus_cost_advantage(data: ManyObjectiveParetoFocusClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Focused search should cost materially less than full-front approximation.

    Standard: arXiv 2604.09417v1 (cs.AI) claim operationalization.
    falsifies_if: focused_search_cost >= full_front_evaluation_cost / 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.focused_search_cost * Fraction(2) < data.full_front_evaluation_cost
    proof = ProofObject(
        rule="check_focus_cost_advantage",
        premises=[
            "paper_id=2604.09417v1",
            f"focused_search_cost={data.focused_search_cost}",
            f"full_front_evaluation_cost={data.full_front_evaluation_cost}",
        ],
        conclusion=(
            "PASS: focused search has clear cost advantage"
            if success else "FAIL: focused search cost advantage is weak"
        ),
    )
    return success, proof

def check_decision_utility_density(data: ManyObjectiveParetoFocusClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Useful decision solutions should be dense in focused region.

    Standard: arXiv 2604.09417v1 (cs.AI) claim operationalization.
    falsifies_if: decision_useful_solution_ratio < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.decision_useful_solution_ratio >= Fraction(3, 4)
    proof = ProofObject(
        rule="check_decision_utility_density",
        premises=[
            "paper_id=2604.09417v1",
            f"decision_useful_solution_ratio={data.decision_useful_solution_ratio}",
            f"hypervolume_ratio={data.hypervolume_ratio}",
        ],
        conclusion=(
            "PASS: focused region contains high utility density"
            if success else "FAIL: focused region utility density is low"
        ),
    )
    return success, proof

def check_knee_regret_bound(data: ManyObjectiveParetoFocusClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Regret at knee solutions should stay below practical bound.

    Standard: arXiv 2604.09417v1 (cs.AI) claim operationalization.
    falsifies_if: knee_region_regret > 1/10 OR sample_efficiency_gain <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = (data.knee_region_regret <= Fraction(1, 10)) and (data.sample_efficiency_gain > Fraction(0))
    proof = ProofObject(
        rule="check_knee_regret_bound",
        premises=[
            "paper_id=2604.09417v1",
            f"knee_region_regret={data.knee_region_regret}",
            f"sample_efficiency_gain={data.sample_efficiency_gain}",
        ],
        conclusion=(
            "PASS: knee regret bound and efficiency gain both hold"
            if success else "FAIL: knee regret or efficiency claim not supported"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """
    Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09417v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = ManyObjectiveParetoFocusClaim(
        objective_dimension=Fraction(6),
        hypervolume_ratio=Fraction(4, 5),
        knee_region_coverage=Fraction(17, 20),
        full_front_evaluation_cost=Fraction(1_000),
        focused_search_cost=Fraction(420),
        decision_useful_solution_ratio=Fraction(4, 5),
        knee_region_regret=Fraction(1, 20),
        sample_efficiency_gain=Fraction(3, 10),
    )

    checks = [
        ("check_many_objective_regime", check_many_objective_regime),
        ("check_knee_region_priority", check_knee_region_priority),
        ("check_focus_cost_advantage", check_focus_cost_advantage),
        ("check_decision_utility_density", check_decision_utility_density),
        ("check_knee_regret_bound", check_knee_regret_bound),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
