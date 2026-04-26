"""D_ARXIV_BLOCK_ENCODING_DOG domain metadata and claim model.

Paper: arXiv 2604.09538v1 (quant-ph)
Title: "Explicit Block Encoding of Difference-of-Gaussian Operators on a Periodic Grid"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DoGClaim:
    """Structured claim parameters for the DoG block encoding.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    grid_size_n: int
    spatial_dimension_d: int
    grid_spacing_h: Fraction
    subnormalisation_lambda: Fraction
    uses_qram: bool
    uses_signed_amplitude_loading: bool
    success_probability: Fraction
    sigma_1: Fraction
    sigma_2: Fraction
    stencil_width: int
    scaling_order: Fraction


@dataclass(frozen=True)
class DoGEvidence:
    """Evidence bundle for the DoG block encoding verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: DoGClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_BLOCK_ENCODING_DOG",
    "claim_model": "DoGClaim",
    "evidence_model": "DoGEvidence",
    "check_functions": [
        "check_constant_subnormalisation",
        "check_no_black_box_oracles",
        "check_o_h4_scaling",
        "check_success_probability_bounded",
    ],
    "paper_id": "2604.09538v1",
    "paper_title": "Explicit Block Encoding of Difference-of-Gaussian Operators on a Periodic Grid",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
