"""D_ARXIV_LINEARIZABLE_REGISTERS domain metadata and claim model.

Paper: arXiv 2604.05862v1 (cs.DC)
Title: "Communication Requirements for Linearizable Registers"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class LinearizableRegistersClaim:
    """Structured claim parameters for linearizable register communication requirements.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    system_name: str
    is_asynchronous: bool
    process_count: int
    is_linearizable: bool
    preserves_real_time_order: bool
    uses_message_chains: bool
    message_chain_density: Fraction
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
    "claim_model": "LinearizableRegistersClaim",
    "evidence_model": "LinearizableRegistersEvidence",
    "check_functions": [
        "check_linearizability",
        "check_real_time_order_preserved",
        "check_message_chains_required",
        "check_chain_density_threshold",
    ],
    "paper_id": "2604.05862v1",
    "paper_title": "Communication Requirements for Linearizable Registers",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
