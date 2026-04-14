"""arXiv-derived domain invariants for Strategic Algorithmic Monoculture: Experimental Evidence from Coordination Games."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class StrategicMonocultureClaim:
    """Structured claim parameters derived from arXiv paper 2604.09502v1 (cs.AI)."""

    baseline_action_similarity: Fraction
    incentivized_action_similarity: Fraction
    human_similarity_shift: Fraction
    llm_similarity_shift: Fraction
    coordination_payoff_gain: Fraction
    strategy_concentration_index: Fraction
    diversity_preservation_floor: Fraction
    equilibrium_reach_rate: Fraction


def check_strategic_similarity_response(data: StrategicMonocultureClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Strategic incentives should increase similarity beyond baseline monoculture.

    Standard: arXiv 2604.09502v1 (cs.AI) claim operationalization.
    falsifies_if: incentivized_action_similarity <= baseline_action_similarity.

    Returns:
        Tuple of (success, proof).
    """
    success = data.incentivized_action_similarity > data.baseline_action_similarity
    proof = ProofObject(
        rule="check_strategic_similarity_response",
        premises=[
            "paper_id=2604.09502v1",
            f"baseline_action_similarity={data.baseline_action_similarity}",
            f"incentivized_action_similarity={data.incentivized_action_similarity}",
        ],
        conclusion=(
            "PASS: strategic incentives increase monoculture"
            if success else "FAIL: no strategic monoculture response observed"
        ),
    )
    return success, proof

def check_llm_shift_exceeds_human_shift(data: StrategicMonocultureClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: LLM strategic shift should be at least as large as human strategic shift.

    Standard: arXiv 2604.09502v1 (cs.AI) claim operationalization.
    falsifies_if: llm_similarity_shift < human_similarity_shift.

    Returns:
        Tuple of (success, proof).
    """
    success = data.llm_similarity_shift >= data.human_similarity_shift
    proof = ProofObject(
        rule="check_llm_shift_exceeds_human_shift",
        premises=[
            "paper_id=2604.09502v1",
            f"llm_similarity_shift={data.llm_similarity_shift}",
            f"human_similarity_shift={data.human_similarity_shift}",
        ],
        conclusion=(
            "PASS: LLM shift matches or exceeds human shift"
            if success else "FAIL: LLM strategic shift is weaker than human shift"
        ),
    )
    return success, proof

def check_coordination_payoff_positive(data: StrategicMonocultureClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Monoculture shift should produce positive coordination payoff gain.

    Standard: arXiv 2604.09502v1 (cs.AI) claim operationalization.
    falsifies_if: coordination_payoff_gain <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.coordination_payoff_gain > Fraction(0)
    proof = ProofObject(
        rule="check_coordination_payoff_positive",
        premises=[
            "paper_id=2604.09502v1",
            f"coordination_payoff_gain={data.coordination_payoff_gain}",
            f"equilibrium_reach_rate={data.equilibrium_reach_rate}",
        ],
        conclusion=(
            "PASS: strategic monoculture improves payoffs"
            if success else "FAIL: no payoff gain from monoculture shift"
        ),
    )
    return success, proof

def check_concentration_bounded_by_diversity_floor(data: StrategicMonocultureClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Concentration should not collapse below diversity preservation floor.

    Standard: arXiv 2604.09502v1 (cs.AI) claim operationalization.
    falsifies_if: strategy_concentration_index > 1 - diversity_preservation_floor.

    Returns:
        Tuple of (success, proof).
    """
    success = data.strategy_concentration_index <= (Fraction(1) - data.diversity_preservation_floor)
    proof = ProofObject(
        rule="check_concentration_bounded_by_diversity_floor",
        premises=[
            "paper_id=2604.09502v1",
            f"strategy_concentration_index={data.strategy_concentration_index}",
            f"diversity_preservation_floor={data.diversity_preservation_floor}",
        ],
        conclusion=(
            "PASS: concentration remains bounded by diversity floor"
            if success else "FAIL: concentration exceeds diversity-preserving bound"
        ),
    )
    return success, proof

def check_equilibrium_coordination_rate(data: StrategicMonocultureClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Strategic monoculture should increase equilibrium reach frequency.

    Standard: arXiv 2604.09502v1 (cs.AI) claim operationalization.
    falsifies_if: equilibrium_reach_rate < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.equilibrium_reach_rate >= Fraction(3, 4)
    proof = ProofObject(
        rule="check_equilibrium_coordination_rate",
        premises=[
            "paper_id=2604.09502v1",
            f"equilibrium_reach_rate={data.equilibrium_reach_rate}",
        ],
        conclusion=(
            "PASS: equilibrium coordination rate is high"
            if success else "FAIL: equilibrium coordination rate is too low"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """
    Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09502v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = StrategicMonocultureClaim(
        baseline_action_similarity=Fraction(3, 5),
        incentivized_action_similarity=Fraction(4, 5),
        human_similarity_shift=Fraction(1, 10),
        llm_similarity_shift=Fraction(1, 5),
        coordination_payoff_gain=Fraction(3, 20),
        strategy_concentration_index=Fraction(3, 5),
        diversity_preservation_floor=Fraction(1, 5),
        equilibrium_reach_rate=Fraction(4, 5),
    )

    checks = [
        ("check_strategic_similarity_response", check_strategic_similarity_response),
        ("check_llm_shift_exceeds_human_shift", check_llm_shift_exceeds_human_shift),
        ("check_coordination_payoff_positive", check_coordination_payoff_positive),
        ("check_concentration_bounded_by_diversity_floor", check_concentration_bounded_by_diversity_floor),
        ("check_equilibrium_coordination_rate", check_equilibrium_coordination_rate),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
