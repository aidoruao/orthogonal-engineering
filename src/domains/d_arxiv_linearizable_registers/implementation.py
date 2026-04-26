"""D_ARXIV_LINEARIZABLE_REGISTERS implementation — Communication Requirements for Linearizable Registers.

Paper: arXiv 2604.05862v1 (cs.DC)
Title: "Communication Requirements for Linearizable Registers"

Mathematical Standards:
- Linearizability correctness condition
- Message chains in asynchronous systems
- Real-time order preservation
- DAG structure of executions
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class DistributedSystem:
    """A model of an asynchronous distributed system.

    Falsifies if: system properties are inconsistent.
    falsifies_if: system properties are inconsistent.
    """
    system_name: str
    is_asynchronous: bool
    process_count: int


@dataclass(frozen=True)
class RegisterImplementation:
    """A linearizable register implementation.

    Falsifies if: implementation properties are inconsistent.
    falsifies_if: implementation properties are inconsistent.
    """
    is_linearizable: bool
    preserves_real_time_order: bool
    uses_message_chains: bool
    message_chain_density: Fraction


@dataclass(frozen=True)
class LinearizableRegistersClaim:
    """Structured claim for linearizable register communication requirements.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    system: DistributedSystem
    register: RegisterImplementation
    chain_density_threshold: Fraction


@dataclass(frozen=True)
class LinearizableRegistersEvidence:
    """Evidence bundle for linearizable register verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: LinearizableRegistersClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_LINEARIZABLE_REGISTERS",
    "paper_id": "2604.05862v1",
    "claim_model": "LinearizableRegistersClaim",
    "evidence_model": "LinearizableRegistersEvidence",
    "check_functions": [
        "check_linearizability",
        "check_real_time_order_preserved",
        "check_message_chains_required",
        "check_chain_density_threshold",
    ],
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
