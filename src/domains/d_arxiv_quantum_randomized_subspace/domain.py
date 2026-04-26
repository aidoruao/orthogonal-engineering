"""D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE domain metadata and claim model.

Paper: arXiv 2604.09483v1 (quant-ph)
Title: "Quantum Randomized Subspace Iteration"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QRSIClaim:
    """Structured claim parameters for QRSI.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    hamiltonian_name: str
    degeneracy_g: int
    spectral_gap: Fraction
    branch_count: int
    satisfies_anti_concentration: bool
    uses_haar_randomness: bool
    estimated_dimension: int
    full_eigenspace_spanned: bool
    spectral_gap_preserved: bool


@dataclass(frozen=True)
class QRSIEvidence:
    """Evidence bundle for QRSI verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: QRSIClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE",
    "claim_model": "QRSIClaim",
    "evidence_model": "QRSIEvidence",
    "check_functions": [
        "check_anti_concentration",
        "check_spectral_gap_preserved",
        "check_full_eigenspace_spanned",
        "check_branch_count_matches_degeneracy",
    ],
    "paper_id": "2604.09483v1",
    "paper_title": "Quantum Randomized Subspace Iteration",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
