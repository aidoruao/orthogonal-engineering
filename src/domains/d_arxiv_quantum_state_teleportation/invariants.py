"""Invariant checks for d_arxiv_quantum_state_teleportation."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumStateTeleportationClaim, create_nominal_claim


def check_fidelity_valid(data: QuantumStateTeleportationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: fidelity must satisfy 0 <= fidelity <= 1.

    Standard: arXiv 2604.07849v1 (quant-ph) claim operationalization.
    Falsifies if: Fidelity is outside [0, 1].
    falsifies_if: fidelity < 0 or fidelity > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.fidelity <= Fraction(1)
    proof = ProofObject(
        rule="check_fidelity_valid",
        premises=[
            "paper_id=2604.07849v1",
            f"fidelity={data.fidelity}",
        ],
        conclusion=(
            "PASS: fidelity in [0, 1]"
            if success else "FAIL: fidelity outside [0, 1]"
        ),
    )
    return success, proof


def check_classical_communication_sufficient(data: QuantumStateTeleportationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: classical_communication_bits must be at least 2.

    Standard: arXiv 2604.07849v1 (quant-ph) claim operationalization.
    Falsifies if: Classical communication bits are less than 2.
    falsifies_if: classical_communication_bits < 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.classical_communication_bits >= Fraction(2)
    proof = ProofObject(
        rule="check_classical_communication_sufficient",
        premises=[
            "paper_id=2604.07849v1",
            f"classical_communication_bits={data.classical_communication_bits}",
        ],
        conclusion=(
            "PASS: classical_communication_bits >= 2"
            if success else "FAIL: classical_communication_bits is less than 2"
        ),
    )
    return success, proof


def check_gate_noise_nonnegative(data: QuantumStateTeleportationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: gate_noise_rate must satisfy 0 <= gate_noise_rate <= 1.

    Standard: arXiv 2604.07849v1 (quant-ph) claim operationalization.
    Falsifies if: Gate noise rate is outside [0, 1].
    falsifies_if: gate_noise_rate < 0 or gate_noise_rate > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.gate_noise_rate <= Fraction(1)
    proof = ProofObject(
        rule="check_gate_noise_nonnegative",
        premises=[
            "paper_id=2604.07849v1",
            f"gate_noise_rate={data.gate_noise_rate}",
        ],
        conclusion=(
            "PASS: gate_noise_rate in [0, 1]"
            if success else "FAIL: gate_noise_rate outside [0, 1]"
        ),
    )
    return success, proof


def check_entanglement_fidelity_valid(data: QuantumStateTeleportationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: entanglement_fidelity must satisfy 0 <= entanglement_fidelity <= 1.

    Standard: arXiv 2604.07849v1 (quant-ph) claim operationalization.
    Falsifies if: Entanglement fidelity is outside [0, 1].
    falsifies_if: entanglement_fidelity < 0 or entanglement_fidelity > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.entanglement_fidelity <= Fraction(1)
    proof = ProofObject(
        rule="check_entanglement_fidelity_valid",
        premises=[
            "paper_id=2604.07849v1",
            f"entanglement_fidelity={data.entanglement_fidelity}",
        ],
        conclusion=(
            "PASS: entanglement_fidelity in [0, 1]"
            if success else "FAIL: entanglement_fidelity outside [0, 1]"
        ),
    )
    return success, proof


def check_teleportation_success(data: QuantumStateTeleportationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: teleportation_succeeds must be True.

    Standard: arXiv 2604.07849v1 (quant-ph) claim operationalization.
    Falsifies if: Teleportation does not succeed.
    falsifies_if: not teleportation_succeeds.

    Returns:
        Tuple of (success, proof).
    """
    success = data.teleportation_succeeds is True
    proof = ProofObject(
        rule="check_teleportation_success",
        premises=[
            "paper_id=2604.07849v1",
            f"teleportation_succeeds={data.teleportation_succeeds}",
        ],
        conclusion=(
            "PASS: teleportation_succeeds is True"
            if success else "FAIL: teleportation_succeeds is not True"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.07849v1 (quant-ph) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_fidelity_valid", check_fidelity_valid),
        ("check_classical_communication_sufficient", check_classical_communication_sufficient),
        ("check_gate_noise_nonnegative", check_gate_noise_nonnegative),
        ("check_entanglement_fidelity_valid", check_entanglement_fidelity_valid),
        ("check_teleportation_success", check_teleportation_success),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
