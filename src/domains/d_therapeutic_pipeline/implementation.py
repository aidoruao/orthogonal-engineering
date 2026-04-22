"""D_THERAPEUTIC_PIPELINE implementation — Failure modes, interventions, constraints.

Component 2 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction


class FailureMode(Enum):
    """AI↔human failure modes."""
    HALLUCINATION = "hallucination"
    RATIONALIZATION = "rationalization"
    HEDGING = "hedging"
    CONTEXT_OVERFLOW = "context_overflow"
    MODE_COLLAPSE = "mode_collapse"
    REWARD_HACKING = "reward_hacking"
    SAFETY_OVERRIDE = "safety_override"


@dataclass(frozen=True)
class TherapeuticIntervention:
    """Therapeutic intervention parameters.

    falsifies_if: any Fraction field is negative.
    falsifies_if: any Fraction field is negative.
    """
    failure_mode: str
    therapy: str
    constraint_level: Fraction
    context_drift: Fraction
    belief_update_rate: Fraction
    validation_frequency: Fraction
    effectiveness: Fraction


@dataclass(frozen=True)
class ConstraintSystem:
    """Constraint system parameters.

    falsifies_if: current_level or threshold is negative.
    falsifies_if: current_level or threshold is negative.
    """
    source: str
    function: str
    current_level: Fraction
    threshold: Fraction
    is_active: bool


def create_nominal_intervention() -> TherapeuticIntervention:
    """Create nominal therapeutic intervention."""
    return TherapeuticIntervention(
        failure_mode="hallucination",
        therapy="reality_testing",
        constraint_level=Fraction(5, 10),
        context_drift=Fraction(2, 10),
        belief_update_rate=Fraction(3, 10),
        validation_frequency=Fraction(3, 10),
        effectiveness=Fraction(7, 10),
    )


def create_nominal_constraint() -> ConstraintSystem:
    """Create nominal constraint system."""
    return ConstraintSystem(
        source="prefrontal_cortex_analogue",
        function="inhibition",
        current_level=Fraction(5, 10),
        threshold=Fraction(3, 10),
        is_active=True,
    )


DOMAIN_METADATA = {
    "id": "THERAPEUTIC_PIPELINE",
    "claim_model": "TherapeuticIntervention",
    "check_functions": [
        "check_constraint_above_threshold",
        "check_context_drift_bounded",
        "check_belief_update_rate",
        "check_reality_testing_frequency",
    ],
}
