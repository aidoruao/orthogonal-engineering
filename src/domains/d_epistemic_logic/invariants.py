#!/usr/bin/env python3
"""Epistemic Logic Domain Invariants — Knowledge, belief, and justification constraints.

Formal Standards:
- Hintikka S4/S5 epistemic logic
- Gettier problem formalization
- Tracking theory (Nozick)
- Safety theory (Sosa)

Falsifies if:
- Accessibility relation violates frame conditions
- JTB claimed without proper justification
- Gettier cases undetected
- Knowledge claims fail tracking
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Agent,
    BeliefState,
    EpistemicFrame,
    JTBAnalysis,
    Proposition,
    SafetyCondition,
    TrackingCondition,
)


def check_frame_reflexivity(frame: EpistemicFrame, agent_id: str) -> Tuple[bool, ProofObject]:
    """S4/S5 requires reflexive accessibility: w R w for all worlds.
    
    Falsifies if: any world is missing self-accessibility for the agent.
    falsifies_if: any world is missing self-accessibility for the agent.
    """
    for w in frame.worlds:
        accessible = frame.accessibility.get(agent_id, set())
        if w not in accessible:
            return False, ProofObject(
                conclusion=f"VIOLATION: Frame not reflexive for agent {agent_id}",
                premises=[f"World {w} not accessible from itself"],
                rule="epistemic_logic_s4_reflexivity"
            )
    
    return True, ProofObject(
        conclusion="Frame satisfies reflexivity condition",
        premises=[f"Worlds: {len(frame.worlds)}"],
        rule="epistemic_frame_reflexive"
    )


def check_knowledge_necessitation(belief: BeliefState, prop: Proposition, world_id: str) -> Tuple[bool, ProofObject]:
    """Knowledge necessitation: If P is known, P is true.
    
    Falsifies if: belief.knows(prop, world_id) is True while prop.is_true_in(world_id) is False.
    falsifies_if: belief.knows(prop, world_id) is True while prop.is_true_in(world_id) is False.
    """
    claims_knowledge = belief.knows(prop, world_id)
    is_true = prop.is_true_in(world_id)
    
    if claims_knowledge and not is_true:
        return False, ProofObject(
            conclusion="VIOLATION: Knowledge claim for false proposition",
            premises=[
                f"Agent: {belief.agent.agent_id}",
                f"Proposition: {prop.prop_id}",
                "Knowledge implies truth axiom violated"
            ],
            rule="epistemic_logic_knowledge_truth"
        )
    
    return True, ProofObject(
        conclusion="Knowledge claim satisfies truth condition",
        premises=[f"Knowledge claim: {claims_knowledge}", f"Truth: {is_true}"],
        rule="knowledge_truth_axiom"
    )


def check_jtb_completeness(analysis: JTBAnalysis) -> Tuple[bool, ProofObject]:
    """Justified True Belief requires all three components.
    
    Falsifies if: true belief lacks justification or justification strength falls below threshold.
    falsifies_if: true belief lacks justification or justification strength falls below threshold.
    """
    MIN_JUSTIFICATION_STRENGTH = Fraction(1, 2)  # 50%
    
    if analysis.belief and analysis.truth:
        if analysis.justification is None:
            return False, ProofObject(
                conclusion="VIOLATION: True belief without justification",
                premises=[
                    f"Agent: {analysis.agent.agent_id}",
                    f"Proposition: {analysis.proposition.prop_id}",
                    "Missing: justification"
                ],
                rule="jtb_justification_required"
            )
        
        strength = analysis.justification.strength()
        if strength < MIN_JUSTIFICATION_STRENGTH:
            return False, ProofObject(
                conclusion=f"VIOLATION: Justification strength {strength} below threshold",
                premises=[
                    f"Strength: {strength}",
                    f"Threshold: {MIN_JUSTIFICATION_STRENGTH}",
                    f"Evidence count: {len(analysis.justification.evidence)}"
                ],
                rule="jtb_justification_sufficient"
            )
    
    return True, ProofObject(
        conclusion="JTB components satisfied",
        premises=[
            f"Belief: {analysis.belief}",
            f"Truth: {analysis.truth}",
            f"Justified: {analysis.justification is not None}"
        ],
        rule="jtb_complete"
    )


def check_gettier_detection(analysis: JTBAnalysis) -> Tuple[bool, ProofObject]:
    """Detect Gettier cases: JTB that is not knowledge due to luck.
    
    Falsifies if: JTB exists with low justification reliability indicating luck-based belief.
    falsifies_if: JTB exists with low justification reliability indicating luck-based belief.
    """
    if not analysis.is_jtb():
        return True, ProofObject(
            conclusion="Not a JTB case - no Gettier analysis needed",
            premises=["JTB: False"],
            rule="gettier_not_applicable"
        )
    
    # Low reliability + true belief suggests luck
    if analysis.justification and analysis.justification.reliability < Fraction(1, 2):
        return False, ProofObject(
            conclusion="VIOLATION: Gettier case detected - JTB by luck not knowledge",
            premises=[
                f"Justification reliability: {analysis.justification.reliability}",
                "True belief is accidental relative to justification",
                f"Agent: {analysis.agent.agent_id}"
            ],
            rule="gettier_case_identified"
        )
    
    return True, ProofObject(
        conclusion="JTB is not a Gettier case - properly connected to truth",
        premises=[f"Reliability: {analysis.justification.reliability if analysis.justification else 'N/A'}"],
        rule="no_gettier_proper_knowledge"
    )


def check_tracking_sensitivity(tracking: TrackingCondition, analysis: JTBAnalysis) -> Tuple[bool, ProofObject]:
    """Nozick's sensitivity: If P were false, S would not believe P.
    
    Falsifies if: tracking.sensitivity is False for a JTB claim (agent would believe P even if false).
    falsifies_if: tracking.sensitivity is False for a JTB claim (agent would believe P even if false).
    """
    if not analysis.is_jtb():
        return True, ProofObject(
            conclusion="No knowledge claim to track",
            premises=[],
            rule="tracking_not_applicable"
        )
    
    if not tracking.sensitivity:
        return False, ProofObject(
            conclusion="VIOLATION: Knowledge fails sensitivity condition",
            premises=[
                f"Agent: {analysis.agent.agent_id}",
                "Would believe P even if P were false",
                "Tracking condition violated"
            ],
            rule="nozick_sensitivity_condition"
        )
    
    return True, ProofObject(
        conclusion="Knowledge satisfies sensitivity condition",
        premises=["Sensitivity: True"],
        rule="sensitivity_satisfied"
    )


def check_safety_condition(safety: SafetyCondition, threshold: Fraction) -> Tuple[bool, ProofObject]:
    """Safety: Belief could not easily have been false.
    
    Falsifies if: safety.safety_score() < threshold (belief too close to being false).
    falsifies_if: safety.safety_score() < threshold (belief too close to being false).
    """
    score = safety.safety_score()
    
    if score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Belief safety score {score} below threshold {threshold}",
            premises=[
                f"Nearby false beliefs: {safety.nearby_false_beliefs}",
                f"Total nearby worlds: {safety.total_nearby_worlds}",
                f"Safety score: {score}"
            ],
            rule="sosa_safety_condition"
        )
    
    return True, ProofObject(
        conclusion="Belief satisfies safety condition",
        premises=[f"Safety score: {score}", f"Threshold: {threshold}"],
        rule="safety_satisfied"
    )


def run_all_invariants() -> dict:
    """Run all D_EPISTEMIC_LOGIC invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    epistemic_frame = EpistemicFrame(
        worlds=None,
        accessibility=None,
        valuation=None,
    )
    jtb_analysis = JTBAnalysis(
        agent=Agent(
        agent_id=None,
        name=None,
    ),
        proposition=Proposition(
        prop_id=None,
        content=None,
        world_truth=None,
    ),
        world_id=None,
        belief=None,
        truth=None,
        justification=None,
    )
    belief_state = BeliefState(
        agent=Agent(
        agent_id=None,
        name=None,
    ),
        accessible_worlds=None,
        beliefs=None,
    )
    proposition = Proposition(
        prop_id=None,
        content=None,
        world_truth=None,
    )
    safety_condition = SafetyCondition(
        nearby_false_beliefs=None,
        total_nearby_worlds=None,
    )
    tracking_condition = TrackingCondition(
        sensitivity=None,
        adherence=None,
    )

    checks = [
        ("check_frame_reflexivity", lambda: check_frame_reflexivity(epistemic_frame, "EPISTEMI-001")),
        ("check_gettier_detection", lambda: check_gettier_detection(jtb_analysis)),
        ("check_jtb_completeness", lambda: check_jtb_completeness(jtb_analysis)),
        ("check_knowledge_necessitation", lambda: check_knowledge_necessitation(belief_state, proposition, "EPISTEMI-001")),
        ("check_safety_condition", lambda: check_safety_condition(safety_condition, Fraction(1000))),
        ("check_tracking_sensitivity", lambda: check_tracking_sensitivity(tracking_condition, jtb_analysis)),
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
    print("All D_EPISTEMIC_LOGIC invariants: PASS")
