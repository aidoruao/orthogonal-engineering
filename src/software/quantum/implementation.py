"""QUANTUM paradigm implementation — State normalization, unitarity, no-cloning.

Phase 3D of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumState:
    """Quantum state vector with normalization and measurement evidence.

    falsifies_if: state_vector_norm != Fraction(1, 1).
    falsifies_if: error_rate < Fraction(0, 1) or error_rate > Fraction(1, 1).
    """
    num_qubits: int
    state_vector_norm: Fraction
    entanglement_entropy: Fraction
    measurement_probabilities_sum: Fraction
    fidelity: Fraction
    error_rate: Fraction


@dataclass(frozen=True)
class QuantumGate:
    """Quantum gate with unitarity evidence.

    falsifies_if: gate_fidelity < Fraction(0, 1) or gate_fidelity > Fraction(1, 1).
    falsifies_if: num_qubits < 1.
    """
    matrix_dimension: int
    is_unitary: bool
    gate_fidelity: Fraction
    num_qubits: int


@dataclass(frozen=True)
class QuantumCircuit:
    """Quantum circuit with depth and error correction evidence.

    falsifies_if: depth < 1 or gate_count < 1 or qubit_count < 1.
    """
    depth: int
    gate_count: int
    qubit_count: int
    error_corrected: bool
    logical_error_rate: Fraction
    physical_error_rate: Fraction


DOMAIN_METADATA = {
    "id": "QUANTUM_PARADIGM",
    "claim_model": "QuantumState / QuantumGate / QuantumCircuit",
    "check_functions": [
        "check_state_normalization",
        "check_gate_unitarity",
        "check_measurement_probability_conservation",
        "check_no_cloning",
        "check_error_threshold",
        "check_circuit_depth_positive",
    ],
}
