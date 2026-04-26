"""D_ARXIV_NONLOCAL_GAMES domain metadata and claim model.

Paper: arXiv 2604.09458v1 (quant-ph)
Title: "Nonlocal Games Revisited: A Representation-Theoretic Path from Bell Locality to Quantum Pseudo-Telepathy"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class NonlocalGameClaim:
    """Structured claim parameters for nonlocal games.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    game_name: str
    player_count: int
    question_count: int
    answer_count: int
    strategy_type: str
    uses_entanglement: bool
    winning_probability: Fraction
    classical_bound: Fraction
    quantum_bound: Fraction
    no_signaling_bound: Fraction


@dataclass(frozen=True)
class NonlocalGameEvidence:
    """Evidence bundle for nonlocal game verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: NonlocalGameClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_NONLOCAL_GAMES",
    "claim_model": "NonlocalGameClaim",
    "evidence_model": "NonlocalGameEvidence",
    "check_functions": [
        "check_quantum_beats_classical",
        "check_no_signaling_upper_bound",
        "check_entanglement_required",
        "check_winning_probability_bounded",
    ],
    "paper_id": "2604.09458v1",
    "paper_title": "Nonlocal Games Revisited: A Representation-Theoretic Path from Bell Locality to Quantum Pseudo-Telepathy",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
