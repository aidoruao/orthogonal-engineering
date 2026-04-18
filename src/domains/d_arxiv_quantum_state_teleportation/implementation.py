"""Implementation models for d_arxiv_quantum_state_teleportation."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumStateTeleportationClaim:
    """Structured claim parameters derived from arXiv paper 2604.07849v1 (quant-ph)."""

    fidelity: Fraction
    classical_communication_bits: Fraction
    gate_noise_rate: Fraction
    entanglement_fidelity: Fraction
    teleportation_succeeds: bool


def create_nominal_claim() -> QuantumStateTeleportationClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumStateTeleportationClaim(
        fidelity=Fraction(9, 10),
        classical_communication_bits=Fraction(2),
        gate_noise_rate=Fraction(1, 100),
        entanglement_fidelity=Fraction(95, 100),
        teleportation_succeeds=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_STATE_TELEPORTATION",
    "paper_id": "2604.07849v1",
    "claim_model": "QuantumStateTeleportationClaim",
    "check_functions": [
        "check_fidelity_valid",
        "check_classical_communication_sufficient",
        "check_gate_noise_nonnegative",
        "check_entanglement_fidelity_valid",
        "check_teleportation_success",
    ],
}
