"""Implementation models for d_arxiv_seeing_is_believing."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class VisionGuidedPromptRobustnessClaim:
    """Structured claim parameters derived from arXiv paper 2604.09532v1 (cs.AI)."""

    label_noise_rate: Fraction
    visual_semantic_stability: Fraction
    prompt_parameter_stability: Fraction
    noisy_label_reliance: Fraction
    clean_set_accuracy: Fraction
    noisy_set_accuracy: Fraction
    cross_modal_alignment_gain: Fraction
    robustness_margin: Fraction

def create_nominal_claim() -> VisionGuidedPromptRobustnessClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return VisionGuidedPromptRobustnessClaim(
        label_noise_rate=Fraction(2, 5),
        visual_semantic_stability=Fraction(9, 10),
        prompt_parameter_stability=Fraction(7, 10),
        noisy_label_reliance=Fraction(1, 4),
        clean_set_accuracy=Fraction(17, 20),
        noisy_set_accuracy=Fraction(7, 10),
        cross_modal_alignment_gain=Fraction(3, 20),
        robustness_margin=Fraction(1, 10),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_SEEING_IS_BELIEVING",
    "paper_id": "2604.09532v1",
    "claim_model": "VisionGuidedPromptRobustnessClaim",
    "check_functions": [
        "check_visual_signal_dominance",
        "check_noise_reliance_bound",
        "check_noisy_accuracy_floor",
        "check_clean_noisy_gap_control",
        "check_cross_modal_prompt_gain",
    ],
}
