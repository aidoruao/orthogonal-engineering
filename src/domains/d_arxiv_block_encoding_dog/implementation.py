"""D_ARXIV_BLOCK_ENCODING_DOG implementation — Explicit Block Encoding of DoG Operators.

Paper: arXiv 2604.09538v1 (quant-ph)
Title: "Explicit Block Encoding of Difference-of-Gaussian Operators on a Periodic Grid"

Mathematical Standards:
- Linear Combination of Unitaries (LCU) framework
- Block encoding with constant subnormalisation factor λ = 2
- O(h⁴) scaling with grid spacing h
- Discrete Fourier basis diagonalization
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class GridConfig:
    """Configuration for the periodic grid.

    Falsifies if: grid parameters are inconsistent.
    falsifies_if: grid parameters are inconsistent.
    """
    grid_size_n: int
    spatial_dimension_d: int
    grid_spacing_h: Fraction


@dataclass(frozen=True)
class BlockEncoding:
    """A quantum block encoding specification.

    Falsifies if: encoding parameters are inconsistent.
    falsifies_if: encoding parameters are inconsistent.
    """
    subnormalisation_lambda: Fraction
    uses_qram: bool
    uses_signed_amplitude_loading: bool
    success_probability: Fraction


@dataclass(frozen=True)
class DoGOperator:
    """Difference-of-Gaussian operator parameters.

    Falsifies if: operator parameters are inconsistent.
    falsifies_if: operator parameters are inconsistent.
    """
    sigma_1: Fraction
    sigma_2: Fraction
    stencil_width: int


@dataclass(frozen=True)
class DoGClaim:
    """Structured claim for the DoG block encoding.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    grid: GridConfig
    encoding: BlockEncoding
    operator: DoGOperator
    scaling_order: Fraction  # expected O(h^4) scaling


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
    "paper_id": "2604.09538v1",
    "claim_model": "DoGClaim",
    "evidence_model": "DoGEvidence",
    "check_functions": [
        "check_constant_subnormalisation",
        "check_no_black_box_oracles",
        "check_o_h4_scaling",
        "check_success_probability_bounded",
    ],
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
