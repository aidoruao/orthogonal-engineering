"""Implementation models for d_arxiv_three_modalities_two."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MultimodalAccessibilityCoDesignClaim:
    """Structured claim parameters derived from arXiv paper 2604.09426v1 (cs.AI)."""

    audio_modality_coverage: Fraction
    haptic_modality_coverage: Fraction
    textual_modality_coverage: Fraction
    nonvisual_navigation_success_rate: Fraction
    task_completion_rate_blv: Fraction
    co_design_iteration_count: Fraction
    prototype_usability_score: Fraction
    cognitive_load_penalty: Fraction

def create_nominal_claim() -> MultimodalAccessibilityCoDesignClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return MultimodalAccessibilityCoDesignClaim(
        audio_modality_coverage=Fraction(4, 5),
        haptic_modality_coverage=Fraction(3, 4),
        textual_modality_coverage=Fraction(7, 10),
        nonvisual_navigation_success_rate=Fraction(4, 5),
        task_completion_rate_blv=Fraction(3, 4),
        co_design_iteration_count=Fraction(3),
        prototype_usability_score=Fraction(17, 20),
        cognitive_load_penalty=Fraction(1, 4),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_THREE_MODALITIES_TWO",
    "paper_id": "2604.09426v1",
    "claim_model": "MultimodalAccessibilityCoDesignClaim",
    "check_functions": [
        "check_audio_channel_accessibility_floor",
        "check_haptic_channel_accessibility_floor",
        "check_text_channel_accessibility_floor",
        "check_nonvisual_navigation_success",
        "check_co_design_iteration_sufficiency",
    ],
}
