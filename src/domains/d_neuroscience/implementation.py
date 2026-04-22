"""Implementation models for Neuroscience — real computation replacing boolean echoes.

Component 4 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class NeuronState:
    """Structured neuron state for real computational invariants.

    falsifies_if: any potential or time field is not a Fraction.
    falsifies_if: any potential or time field is not a Fraction.
    """
    membrane_potential_mv: Fraction
    threshold_potential_mv: Fraction
    resting_potential_mv: Fraction
    time_since_spike_ms: Fraction
    absolute_refractory_period_ms: Fraction
    relative_refractory_period_ms: Fraction
    synaptic_weight: Fraction
    learning_rate: Fraction
    presynaptic_activity: Fraction
    postsynaptic_activity: Fraction
    memory_strength: Fraction
    time_since_learning: Fraction
    conduction_velocity: Fraction
    myelinated: bool
    unmyelinated_baseline_velocity: Fraction


def create_nominal_state() -> NeuronState:
    """Create nominal neuron state for testing."""
    return NeuronState(
        membrane_potential_mv=Fraction(-50, 1),
        threshold_potential_mv=Fraction(-55, 1),
        resting_potential_mv=Fraction(-70, 1),
        time_since_spike_ms=Fraction(5, 1),
        absolute_refractory_period_ms=Fraction(1, 1),
        relative_refractory_period_ms=Fraction(3, 1),
        synaptic_weight=Fraction(5, 10),
        learning_rate=Fraction(1, 100),
        presynaptic_activity=Fraction(10, 1),
        postsynaptic_activity=Fraction(8, 1),
        memory_strength=Fraction(10, 1),
        time_since_learning=Fraction(2, 1),
        conduction_velocity=Fraction(120, 1),
        myelinated=True,
        unmyelinated_baseline_velocity=Fraction(1, 1),
    )


DOMAIN_METADATA = {
    "id": "NEUROSCIENCE",
    "claim_model": "NeuronState",
    "check_functions": [
        "check_action_potential_threshold",
        "check_synaptic_weight_hebbian_update",
        "check_refractory_period_timing",
        "check_ebbinghaus_retention",
        "check_myelination_conduction_boost",
    ],
}
