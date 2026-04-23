"""Test suite for quantum paradigm invariants.

Phase 3D of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.software.quantum.invariants import (
    check_state_normalization,
    check_gate_unitarity,
    check_measurement_probability_conservation,
    check_no_cloning,
    check_error_threshold,
    check_circuit_depth_positive,
    run_all_invariants,
)
from src.software.quantum.implementation import QuantumState, QuantumGate, QuantumCircuit


class TestQuantum:
    def test_pass_cases(self):
        state = QuantumState(
            num_qubits=2, state_vector_norm=Fraction(1, 1),
            entanglement_entropy=Fraction(1, 2),
            measurement_probabilities_sum=Fraction(1, 1),
            fidelity=Fraction(99, 100), error_rate=Fraction(1, 100),
        )
        gate = QuantumGate(
            matrix_dimension=4, is_unitary=True,
            gate_fidelity=Fraction(99, 100), num_qubits=2,
        )
        circuit = QuantumCircuit(
            depth=3, gate_count=5, qubit_count=2, error_corrected=True,
            logical_error_rate=Fraction(1, 1000), physical_error_rate=Fraction(1, 100),
        )
        assert check_state_normalization(state)[0] is True
        assert check_gate_unitarity(gate)[0] is True
        assert check_measurement_probability_conservation(state)[0] is True
        assert check_no_cloning(state)[0] is True
        assert check_error_threshold(circuit)[0] is True
        assert check_circuit_depth_positive(circuit)[0] is True

    def test_fail_cases(self):
        state = QuantumState(
            num_qubits=2, state_vector_norm=Fraction(99, 100),
            entanglement_entropy=Fraction(1, 2),
            measurement_probabilities_sum=Fraction(101, 100),
            fidelity=Fraction(1, 1), error_rate=Fraction(1, 100),
        )
        gate = QuantumGate(
            matrix_dimension=4, is_unitary=False,
            gate_fidelity=Fraction(99, 100), num_qubits=2,
        )
        circuit = QuantumCircuit(
            depth=0, gate_count=0, qubit_count=0, error_corrected=True,
            logical_error_rate=Fraction(1, 10), physical_error_rate=Fraction(1, 100),
        )
        assert check_state_normalization(state)[0] is False
        assert check_gate_unitarity(gate)[0] is False
        assert check_measurement_probability_conservation(state)[0] is False
        assert check_no_cloning(state)[0] is False
        assert check_error_threshold(circuit)[0] is False
        assert check_circuit_depth_positive(circuit)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
