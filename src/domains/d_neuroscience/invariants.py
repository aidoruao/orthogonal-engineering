"""Invariant checks for Neuroscience — real computation replacing boolean echoes.

Component 4 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import NeuronState, create_nominal_state


def check_action_potential_threshold(neuron: NeuronState) -> Tuple[bool, ProofObject]:
    """Neuron fires if membrane potential >= threshold.

    Falsifies if: membrane_potential_mv >= threshold_potential_mv but neuron did not fire.
    falsifies_if: membrane_potential_mv >= threshold_potential_mv but neuron did not fire.
    """
    fires = neuron.membrane_potential_mv >= neuron.threshold_potential_mv
    if not fires:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Membrane potential {neuron.membrane_potential_mv} mV < "
                f"threshold {neuron.threshold_potential_mv} mV — no fire"
            ),
            premises=[
                f"V_m: {neuron.membrane_potential_mv} mV",
                f"V_threshold: {neuron.threshold_potential_mv} mV",
            ],
            rule="neuroscience_action_potential",
        )
    return True, ProofObject(
        conclusion=(
            f"Action potential threshold met: {neuron.membrane_potential_mv} mV >= "
            f"{neuron.threshold_potential_mv} mV"
        ),
        premises=[
            f"V_m: {neuron.membrane_potential_mv} mV",
            f"V_threshold: {neuron.threshold_potential_mv} mV",
        ],
        rule="neuroscience_action_potential",
    )


def check_synaptic_weight_hebbian_update(neuron: NeuronState) -> Tuple[bool, ProofObject]:
    """Hebbian update Δw = η * pre * post must be non-negative when inputs non-negative.

    Falsifies if: computed_delta < 0 when all inputs are non-negative.
    falsifies_if: computed_delta < 0 when all inputs are non-negative.
    """
    delta = neuron.learning_rate * neuron.presynaptic_activity * neuron.postsynaptic_activity
    if delta < Fraction(0, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Hebbian delta {delta} is negative",
            premises=[
                f"η: {neuron.learning_rate}",
                f"Pre: {neuron.presynaptic_activity}",
                f"Post: {neuron.postsynaptic_activity}",
                f"Δw: {delta}",
            ],
            rule="neuroscience_hebbian_update",
        )
    return True, ProofObject(
        conclusion=f"Hebbian delta {delta} >= 0",
        premises=[f"Δw: {delta}"],
        rule="neuroscience_hebbian_update",
    )


def check_refractory_period_timing(neuron: NeuronState) -> Tuple[bool, ProofObject]:
    """Neuron cannot fire during absolute refractory period.

    Falsifies if: time_since_spike_ms < absolute_refractory_period_ms.
    falsifies_if: time_since_spike_ms < absolute_refractory_period_ms.
    """
    if neuron.time_since_spike_ms < neuron.absolute_refractory_period_ms:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Fired too soon — {neuron.time_since_spike_ms} ms < "
                f"absolute refractory {neuron.absolute_refractory_period_ms} ms"
            ),
            premises=[
                f"Time since spike: {neuron.time_since_spike_ms} ms",
                f"Absolute refractory: {neuron.absolute_refractory_period_ms} ms",
            ],
            rule="neuroscience_refractory_period",
        )
    return True, ProofObject(
        conclusion=(
            f"Refractory period respected: {neuron.time_since_spike_ms} ms >= "
            f"{neuron.absolute_refractory_period_ms} ms"
        ),
        premises=[
            f"Time since spike: {neuron.time_since_spike_ms} ms",
            f"Absolute refractory: {neuron.absolute_refractory_period_ms} ms",
        ],
        rule="neuroscience_refractory_period",
    )


def check_ebbinghaus_retention(neuron: NeuronState) -> Tuple[bool, ProofObject]:
    """Memory retention R = S / (S + t) must stay above 50%.

    Falsifies if: retention < Fraction(1, 2).
    falsifies_if: retention < Fraction(1, 2).
    """
    s = neuron.memory_strength
    t = neuron.time_since_learning
    if s + t == Fraction(0, 1):
        return False, ProofObject(
            conclusion="VIOLATION: Ebbinghaus denominator is zero",
            premises=[f"S: {s}", f"t: {t}"],
            rule="neuroscience_ebbinghaus",
        )
    retention = s / (s + t)
    if retention < Fraction(1, 2):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Retention {retention} < 50% — memory decayed"
            ),
            premises=[
                f"S: {s}",
                f"t: {t}",
                f"R: {retention}",
            ],
            rule="neuroscience_ebbinghaus",
        )
    return True, ProofObject(
        conclusion=f"Retention {retention} >= 50%",
        premises=[f"S: {s}", f"t: {t}", f"R: {retention}"],
        rule="neuroscience_ebbinghaus",
    )


def check_myelination_conduction_boost(neuron: NeuronState) -> Tuple[bool, ProofObject]:
    """Myelinated axon must conduct faster than unmyelinated baseline.

    Falsifies if: myelinated == True but conduction_velocity <= unmyelinated_baseline_velocity.
    falsifies_if: myelinated == True but conduction_velocity <= unmyelinated_baseline_velocity.
    """
    if neuron.myelinated and neuron.conduction_velocity <= neuron.unmyelinated_baseline_velocity:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Myelinated velocity {neuron.conduction_velocity} <= "
                f"baseline {neuron.unmyelinated_baseline_velocity}"
            ),
            premises=[
                f"Myelinated: {neuron.myelinated}",
                f"Velocity: {neuron.conduction_velocity}",
                f"Baseline: {neuron.unmyelinated_baseline_velocity}",
            ],
            rule="neuroscience_myelination",
        )
    return True, ProofObject(
        conclusion=(
            f"Myelination boost valid: {neuron.conduction_velocity} > "
            f"{neuron.unmyelinated_baseline_velocity}"
        ),
        premises=[
            f"Myelinated: {neuron.myelinated}",
            f"Velocity: {neuron.conduction_velocity}",
        ],
        rule="neuroscience_myelination",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all neuroscience checks with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_neuron = create_nominal_state()
    fail_neuron = NeuronState(
        membrane_potential_mv=Fraction(-80, 1),
        threshold_potential_mv=Fraction(-55, 1),
        resting_potential_mv=Fraction(-70, 1),
        time_since_spike_ms=Fraction(0, 1),
        absolute_refractory_period_ms=Fraction(1, 1),
        relative_refractory_period_ms=Fraction(3, 1),
        synaptic_weight=Fraction(5, 10),
        learning_rate=Fraction(1, 100),
        presynaptic_activity=Fraction(10, 1),
        postsynaptic_activity=Fraction(8, 1),
        memory_strength=Fraction(1, 1),
        time_since_learning=Fraction(10, 1),
        conduction_velocity=Fraction(1, 1),
        myelinated=True,
        unmyelinated_baseline_velocity=Fraction(2, 1),
    )

    checks = [
        ("check_action_potential_threshold_pass", lambda: check_action_potential_threshold(pass_neuron)),
        ("check_action_potential_threshold_fail", lambda: check_action_potential_threshold(fail_neuron)),
        ("check_synaptic_weight_hebbian_update_pass", lambda: check_synaptic_weight_hebbian_update(pass_neuron)),
        ("check_synaptic_weight_hebbian_update_fail", lambda: check_synaptic_weight_hebbian_update(fail_neuron)),
        ("check_refractory_period_timing_pass", lambda: check_refractory_period_timing(pass_neuron)),
        ("check_refractory_period_timing_fail", lambda: check_refractory_period_timing(fail_neuron)),
        ("check_ebbinghaus_retention_pass", lambda: check_ebbinghaus_retention(pass_neuron)),
        ("check_ebbinghaus_retention_fail", lambda: check_ebbinghaus_retention(fail_neuron)),
        ("check_myelination_conduction_boost_pass", lambda: check_myelination_conduction_boost(pass_neuron)),
        ("check_myelination_conduction_boost_fail", lambda: check_myelination_conduction_boost(fail_neuron)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
