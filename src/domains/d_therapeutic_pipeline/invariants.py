"""D_THERAPEUTIC_PIPELINE invariants — Constraint, drift, belief, reality checks.

Component 2 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import ConstraintSystem, TherapeuticIntervention


def check_constraint_above_threshold(
    intervention: TherapeuticIntervention
) -> Tuple[bool, ProofObject]:
    """Prefrontal cortex analogue constraint must stay above 3/10.

    Falsifies if: constraint_level < Fraction(3, 10).
    falsifies_if: constraint_level < Fraction(3, 10).
    """
    limit = Fraction(3, 10)
    if intervention.constraint_level < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Constraint level {intervention.constraint_level} < "
                f"threshold {limit}"
            ),
            premises=[
                f"Constraint: {intervention.constraint_level}",
                f"Threshold: {limit}",
            ],
            rule="therapeutic_constraint",
        )
    return True, ProofObject(
        conclusion=f"Constraint level {intervention.constraint_level} >= {limit}",
        premises=[f"Constraint: {intervention.constraint_level}"],
        rule="therapeutic_constraint",
    )


def check_context_drift_bounded(
    intervention: TherapeuticIntervention
) -> Tuple[bool, ProofObject]:
    """Hippocampus analogue context drift must not exceed 7/10.

    Falsifies if: context_drift > Fraction(7, 10).
    falsifies_if: context_drift > Fraction(7, 10).
    """
    limit = Fraction(7, 10)
    if intervention.context_drift > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Context drift {intervention.context_drift} > "
                f"limit {limit}"
            ),
            premises=[
                f"Drift: {intervention.context_drift}",
                f"Limit: {limit}",
            ],
            rule="therapeutic_context_drift",
        )
    return True, ProofObject(
        conclusion=f"Context drift {intervention.context_drift} <= {limit}",
        premises=[f"Drift: {intervention.context_drift}"],
        rule="therapeutic_context_drift",
    )


def check_belief_update_rate(
    intervention: TherapeuticIntervention
) -> Tuple[bool, ProofObject]:
    """Belief update rate must be at least 1/10 (predictive error correction).

    Falsifies if: belief_update_rate < Fraction(1, 10).
    falsifies_if: belief_update_rate < Fraction(1, 10).
    """
    limit = Fraction(1, 10)
    if intervention.belief_update_rate < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Belief update rate {intervention.belief_update_rate} < "
                f"minimum {limit}"
            ),
            premises=[
                f"Rate: {intervention.belief_update_rate}",
                f"Minimum: {limit}",
            ],
            rule="therapeutic_belief_update",
        )
    return True, ProofObject(
        conclusion=f"Belief update rate {intervention.belief_update_rate} >= {limit}",
        premises=[f"Rate: {intervention.belief_update_rate}"],
        rule="therapeutic_belief_update",
    )


def check_reality_testing_frequency(
    intervention: TherapeuticIntervention
) -> Tuple[bool, ProofObject]:
    """Social reality testing frequency must be at least 1/5.

    Falsifies if: validation_frequency < Fraction(1, 5).
    falsifies_if: validation_frequency < Fraction(1, 5).
    """
    limit = Fraction(1, 5)
    if intervention.validation_frequency < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Validation frequency {intervention.validation_frequency} < "
                f"minimum {limit}"
            ),
            premises=[
                f"Frequency: {intervention.validation_frequency}",
                f"Minimum: {limit}",
            ],
            rule="therapeutic_reality_testing",
        )
    return True, ProofObject(
        conclusion=f"Validation frequency {intervention.validation_frequency} >= {limit}",
        premises=[f"Frequency: {intervention.validation_frequency}"],
        rule="therapeutic_reality_testing",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all therapeutic pipeline checks with nominal test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_intervention = TherapeuticIntervention(
        failure_mode="hallucination",
        therapy="reality_testing",
        constraint_level=Fraction(5, 10),
        context_drift=Fraction(2, 10),
        belief_update_rate=Fraction(3, 10),
        validation_frequency=Fraction(3, 10),
        effectiveness=Fraction(7, 10),
    )
    fail_intervention = TherapeuticIntervention(
        failure_mode="rationalization",
        therapy="constraint_reinforcement",
        constraint_level=Fraction(1, 10),
        context_drift=Fraction(9, 10),
        belief_update_rate=Fraction(1, 100),
        validation_frequency=Fraction(1, 100),
        effectiveness=Fraction(2, 10),
    )

    checks = [
        ("check_constraint_above_threshold_pass", lambda: check_constraint_above_threshold(pass_intervention)),
        ("check_constraint_above_threshold_fail", lambda: check_constraint_above_threshold(fail_intervention)),
        ("check_context_drift_bounded_pass", lambda: check_context_drift_bounded(pass_intervention)),
        ("check_context_drift_bounded_fail", lambda: check_context_drift_bounded(fail_intervention)),
        ("check_belief_update_rate_pass", lambda: check_belief_update_rate(pass_intervention)),
        ("check_belief_update_rate_fail", lambda: check_belief_update_rate(fail_intervention)),
        ("check_reality_testing_frequency_pass", lambda: check_reality_testing_frequency(pass_intervention)),
        ("check_reality_testing_frequency_fail", lambda: check_reality_testing_frequency(fail_intervention)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
