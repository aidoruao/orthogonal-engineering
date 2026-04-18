"""Implementation models for d_arxiv_statml_bi_lipschitz."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class BiLipschitzAutoencoderClaim:
    """Structured claim parameters derived from arXiv paper 2604.06701v1 (stat.ML)."""

    input_dimension: Fraction
    latent_dimension: Fraction
    lipschitz_constant: Fraction
    bi_lipschitz_lower: Fraction
    is_injective: bool


def create_nominal_claim() -> BiLipschitzAutoencoderClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return BiLipschitzAutoencoderClaim(
        input_dimension=Fraction(100),
        latent_dimension=Fraction(10),
        lipschitz_constant=Fraction(2),
        bi_lipschitz_lower=Fraction(1, 2),
        is_injective=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_BI_LIPSCHITZ",
    "paper_id": "2604.06701v1",
    "claim_model": "BiLipschitzAutoencoderClaim",
    "check_functions": [
        "check_injectivity",
        "check_lipschitz_constant_valid",
        "check_dimension_valid",
        "check_bi_lipschitz_lower_positive",
        "check_input_dimension_positive",
    ],
}
