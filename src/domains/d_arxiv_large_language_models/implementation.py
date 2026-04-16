"""Implementation models for d_arxiv_large_language_models."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class HarmMechanismClaim:
    """Structured claim parameters derived from arXiv paper 2604.09544v1 (cs.AI)."""

    total_model_weights: Fraction
    harmful_mechanism_weights: Fraction
    benign_capability_weights: Fraction
    harm_benign_overlap_ratio: Fraction
    harm_output_after_targeted_prune: Fraction
    benign_output_after_targeted_prune: Fraction
    cross_harm_transfer_ratio: Fraction
    alignment_feature_shift: Fraction

def create_nominal_claim() -> HarmMechanismClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return HarmMechanismClaim(
        total_model_weights=Fraction(10_000),
        harmful_mechanism_weights=Fraction(800),
        benign_capability_weights=Fraction(6_500),
        harm_benign_overlap_ratio=Fraction(1, 10),
        harm_output_after_targeted_prune=Fraction(2, 5),
        benign_output_after_targeted_prune=Fraction(9, 10),
        cross_harm_transfer_ratio=Fraction(4, 5),
        alignment_feature_shift=Fraction(1, 10),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_LARGE_LANGUAGE_MODELS",
    "paper_id": "2604.09544v1",
    "claim_model": "HarmMechanismClaim",
    "check_functions": [
        "check_harm_weight_compactness",
        "check_harm_benign_mechanism_separation",
        "check_targeted_pruning_selectivity",
        "check_cross_harm_generalization",
        "check_alignment_feature_localization",
    ],
}
