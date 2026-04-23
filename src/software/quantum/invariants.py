"""QUANTUM paradigm invariants — Born, von Neumann, Gleason, no-cloning, threshold.

Phase 3D of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import QuantumState, QuantumGate, QuantumCircuit


def check_state_normalization(state: QuantumState) -> Tuple[bool, ProofObject]:
    """State vector must have norm 1 (Born 1926).

    Falsifies if: state_vector_norm != Fraction(1, 1).
    falsifies_if: state_vector_norm != Fraction(1, 1).
    """
    if state.state_vector_norm != Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: State norm {state.state_vector_norm} != 1",
            premises=[f"Norm: {state.state_vector_norm}"],
            rule="quantum_state_normalization",
        )
    return True, ProofObject(
        conclusion=f"State normalized: norm={state.state_vector_norm}",
        premises=[f"Norm: {state.state_vector_norm}"],
        rule="quantum_state_normalization",
    )


def check_gate_unitarity(gate: QuantumGate) -> Tuple[bool, ProofObject]:
    """Quantum gates must be unitary (von Neumann 1932).

    Falsifies if: is_unitary == False.
    falsifies_if: is_unitary == False.
    """
    if not gate.is_unitary:
        return False, ProofObject(
            conclusion="VIOLATION: Gate is not unitary",
            premises=[f"Unitary: {gate.is_unitary}"],
            rule="quantum_gate_unitarity",
        )
    return True, ProofObject(
        conclusion="Gate is unitary",
        premises=[f"Unitary: {gate.is_unitary}"],
        rule="quantum_gate_unitarity",
    )


def check_measurement_probability_conservation(state: QuantumState) -> Tuple[bool, ProofObject]:
    """Measurement probabilities must sum to 1 (Gleason 1957).

    Falsifies if: measurement_probabilities_sum != Fraction(1, 1).
    falsifies_if: measurement_probabilities_sum != Fraction(1, 1).
    """
    if state.measurement_probabilities_sum != Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Probability sum {state.measurement_probabilities_sum} != 1",
            premises=[f"Sum: {state.measurement_probabilities_sum}"],
            rule="quantum_measurement_conservation",
        )
    return True, ProofObject(
        conclusion=f"Probability conserved: sum={state.measurement_probabilities_sum}",
        premises=[f"Sum: {state.measurement_probabilities_sum}"],
        rule="quantum_measurement_conservation",
    )


def check_no_cloning(state: QuantumState) -> Tuple[bool, ProofObject]:
    """No-cloning theorem: perfect cloning of entangled state is impossible.

    Falsifies if: fidelity == 1 AND num_qubits > 1 AND entanglement_entropy > 0.
    falsifies_if: fidelity == Fraction(1, 1) and num_qubits > 1 and entanglement_entropy > Fraction(0, 1).
    """
    if (
        state.fidelity == Fraction(1, 1)
        and state.num_qubits > 1
        and state.entanglement_entropy > Fraction(0, 1)
    ):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: No-cloning theorem violated — "
                f"fidelity={state.fidelity}, qubits={state.num_qubits}, entropy={state.entanglement_entropy}"
            ),
            premises=[
                f"Fidelity: {state.fidelity}",
                f"Qubits: {state.num_qubits}",
                f"Entropy: {state.entanglement_entropy}",
            ],
            rule="quantum_no_cloning",
        )
    return True, ProofObject(
        conclusion=(
            f"No-cloning respected: fidelity={state.fidelity}, qubits={state.num_qubits}, entropy={state.entanglement_entropy}"
        ),
        premises=[
            f"Fidelity: {state.fidelity}",
            f"Qubits: {state.num_qubits}",
        ],
        rule="quantum_no_cloning",
    )


def check_error_threshold(circuit: QuantumCircuit) -> Tuple[bool, ProofObject]:
    """Threshold theorem: logical error < physical error when corrected.

    Falsifies if: error_corrected AND logical_error_rate >= physical_error_rate.
    falsifies_if: error_corrected and logical_error_rate >= physical_error_rate.
    """
    if circuit.error_corrected and circuit.logical_error_rate >= circuit.physical_error_rate:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Error threshold not met — logical {circuit.logical_error_rate} >= physical {circuit.physical_error_rate}"
            ),
            premises=[
                f"Logical: {circuit.logical_error_rate}",
                f"Physical: {circuit.physical_error_rate}",
                f"Corrected: {circuit.error_corrected}",
            ],
            rule="quantum_error_threshold",
        )
    return True, ProofObject(
        conclusion=f"Error threshold valid: logical={circuit.logical_error_rate}, physical={circuit.physical_error_rate}",
        premises=[
            f"Logical: {circuit.logical_error_rate}",
            f"Physical: {circuit.physical_error_rate}",
        ],
        rule="quantum_error_threshold",
    )


def check_circuit_depth_positive(circuit: QuantumCircuit) -> Tuple[bool, ProofObject]:
    """Circuit model: depth, gate_count, qubit_count must all be >= 1 (Deutsch 1989).

    Falsifies if: depth < 1 OR gate_count < 1 OR qubit_count < 1.
    falsifies_if: depth < 1 or gate_count < 1 or qubit_count < 1.
    """
    if circuit.depth < 1 or circuit.gate_count < 1 or circuit.qubit_count < 1:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Invalid circuit dimensions — depth={circuit.depth}, gates={circuit.gate_count}, qubits={circuit.qubit_count}"
            ),
            premises=[
                f"Depth: {circuit.depth}",
                f"Gates: {circuit.gate_count}",
                f"Qubits: {circuit.qubit_count}",
            ],
            rule="quantum_circuit_depth",
        )
    return True, ProofObject(
        conclusion=(
            f"Circuit valid: depth={circuit.depth}, gates={circuit.gate_count}, qubits={circuit.qubit_count}"
        ),
        premises=[
            f"Depth: {circuit.depth}",
            f"Gates: {circuit.gate_count}",
            f"Qubits: {circuit.qubit_count}",
        ],
        rule="quantum_circuit_depth",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all quantum paradigm checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_state = QuantumState(
        num_qubits=2,
        state_vector_norm=Fraction(1, 1),
        entanglement_entropy=Fraction(1, 2),
        measurement_probabilities_sum=Fraction(1, 1),
        fidelity=Fraction(99, 100),
        error_rate=Fraction(1, 100),
    )
    fail_state = QuantumState(
        num_qubits=2,
        state_vector_norm=Fraction(99, 100),
        entanglement_entropy=Fraction(1, 2),
        measurement_probabilities_sum=Fraction(101, 100),
        fidelity=Fraction(1, 1),
        error_rate=Fraction(1, 100),
    )
    pass_gate = QuantumGate(
        matrix_dimension=4, is_unitary=True, gate_fidelity=Fraction(99, 100), num_qubits=2,
    )
    fail_gate = QuantumGate(
        matrix_dimension=4, is_unitary=False, gate_fidelity=Fraction(99, 100), num_qubits=2,
    )
    pass_circuit = QuantumCircuit(
        depth=3, gate_count=5, qubit_count=2, error_corrected=True,
        logical_error_rate=Fraction(1, 1000), physical_error_rate=Fraction(1, 100),
    )
    fail_circuit = QuantumCircuit(
        depth=0, gate_count=0, qubit_count=0, error_corrected=True,
        logical_error_rate=Fraction(1, 10), physical_error_rate=Fraction(1, 100),
    )

    checks = [
        ("check_state_normalization_pass", lambda: check_state_normalization(pass_state)),
        ("check_state_normalization_fail", lambda: check_state_normalization(fail_state)),
        ("check_gate_unitarity_pass", lambda: check_gate_unitarity(pass_gate)),
        ("check_gate_unitarity_fail", lambda: check_gate_unitarity(fail_gate)),
        ("check_measurement_probability_conservation_pass", lambda: check_measurement_probability_conservation(pass_state)),
        ("check_measurement_probability_conservation_fail", lambda: check_measurement_probability_conservation(fail_state)),
        ("check_no_cloning_pass", lambda: check_no_cloning(pass_state)),
        ("check_no_cloning_fail", lambda: check_no_cloning(fail_state)),
        ("check_error_threshold_pass", lambda: check_error_threshold(pass_circuit)),
        ("check_error_threshold_fail", lambda: check_error_threshold(fail_circuit)),
        ("check_circuit_depth_positive_pass", lambda: check_circuit_depth_positive(pass_circuit)),
        ("check_circuit_depth_positive_fail", lambda: check_circuit_depth_positive(fail_circuit)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
