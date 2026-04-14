"""arXiv-derived domain invariants for Three Modalities, Two Design Probes, One Prototype, and No Vision: Experience-Based Co-Design of a Multi-modal 3D Data Visualization Tool."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject


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


def check_audio_channel_accessibility_floor(data: MultimodalAccessibilityCoDesignClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Audio modality should provide strong access coverage.

    Standard: arXiv 2604.09426v1 (cs.AI) claim operationalization.
    falsifies_if: audio_modality_coverage < 2/3.

    Returns:
        Tuple of (success, proof).
    """
    success = data.audio_modality_coverage >= Fraction(2, 3)
    proof = ProofObject(
        rule="check_audio_channel_accessibility_floor",
        premises=[
            "paper_id=2604.09426v1",
            f"audio_modality_coverage={data.audio_modality_coverage}",
        ],
        conclusion=(
            "PASS: audio channel coverage is sufficient"
            if success else "FAIL: audio channel coverage is insufficient"
        ),
    )
    return success, proof

def check_haptic_channel_accessibility_floor(data: MultimodalAccessibilityCoDesignClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Haptic modality should provide strong access coverage.

    Standard: arXiv 2604.09426v1 (cs.AI) claim operationalization.
    falsifies_if: haptic_modality_coverage < 2/3.

    Returns:
        Tuple of (success, proof).
    """
    success = data.haptic_modality_coverage >= Fraction(2, 3)
    proof = ProofObject(
        rule="check_haptic_channel_accessibility_floor",
        premises=[
            "paper_id=2604.09426v1",
            f"haptic_modality_coverage={data.haptic_modality_coverage}",
        ],
        conclusion=(
            "PASS: haptic channel coverage is sufficient"
            if success else "FAIL: haptic channel coverage is insufficient"
        ),
    )
    return success, proof

def check_text_channel_accessibility_floor(data: MultimodalAccessibilityCoDesignClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Text modality should provide strong access coverage.

    Standard: arXiv 2604.09426v1 (cs.AI) claim operationalization.
    falsifies_if: textual_modality_coverage < 2/3.

    Returns:
        Tuple of (success, proof).
    """
    success = data.textual_modality_coverage >= Fraction(2, 3)
    proof = ProofObject(
        rule="check_text_channel_accessibility_floor",
        premises=[
            "paper_id=2604.09426v1",
            f"textual_modality_coverage={data.textual_modality_coverage}",
        ],
        conclusion=(
            "PASS: text channel coverage is sufficient"
            if success else "FAIL: text channel coverage is insufficient"
        ),
    )
    return success, proof

def check_nonvisual_navigation_success(data: MultimodalAccessibilityCoDesignClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: BLV users should navigate 3D visualizations without vision reliably.

    Standard: arXiv 2604.09426v1 (cs.AI) claim operationalization.
    falsifies_if: nonvisual_navigation_success_rate < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.nonvisual_navigation_success_rate >= Fraction(3, 4)
    proof = ProofObject(
        rule="check_nonvisual_navigation_success",
        premises=[
            "paper_id=2604.09426v1",
            f"nonvisual_navigation_success_rate={data.nonvisual_navigation_success_rate}",
            f"task_completion_rate_blv={data.task_completion_rate_blv}",
        ],
        conclusion=(
            "PASS: nonvisual navigation success is high"
            if success else "FAIL: nonvisual navigation success is too low"
        ),
    )
    return success, proof

def check_co_design_iteration_sufficiency(data: MultimodalAccessibilityCoDesignClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Experience-based co-design must include repeated iteration with BLV stakeholders.

    Standard: arXiv 2604.09426v1 (cs.AI) claim operationalization.
    falsifies_if: co_design_iteration_count < 2 OR prototype_usability_score < 3/4 OR cognitive_load_penalty > 1/3.

    Returns:
        Tuple of (success, proof).
    """
    success = (data.co_design_iteration_count >= Fraction(2)) and (data.prototype_usability_score >= Fraction(3, 4)) and (data.cognitive_load_penalty <= Fraction(1, 3))
    proof = ProofObject(
        rule="check_co_design_iteration_sufficiency",
        premises=[
            "paper_id=2604.09426v1",
            f"co_design_iteration_count={data.co_design_iteration_count}",
            f"prototype_usability_score={data.prototype_usability_score}",
            f"cognitive_load_penalty={data.cognitive_load_penalty}",
        ],
        conclusion=(
            "PASS: co-design iterations produce usable low-load prototype"
            if success else "FAIL: co-design process or prototype usability is insufficient"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """
    Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09426v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = MultimodalAccessibilityCoDesignClaim(
        audio_modality_coverage=Fraction(4, 5),
        haptic_modality_coverage=Fraction(3, 4),
        textual_modality_coverage=Fraction(7, 10),
        nonvisual_navigation_success_rate=Fraction(4, 5),
        task_completion_rate_blv=Fraction(3, 4),
        co_design_iteration_count=Fraction(3),
        prototype_usability_score=Fraction(17, 20),
        cognitive_load_penalty=Fraction(1, 4),
    )

    checks = [
        ("check_audio_channel_accessibility_floor", check_audio_channel_accessibility_floor),
        ("check_haptic_channel_accessibility_floor", check_haptic_channel_accessibility_floor),
        ("check_text_channel_accessibility_floor", check_text_channel_accessibility_floor),
        ("check_nonvisual_navigation_success", check_nonvisual_navigation_success),
        ("check_co_design_iteration_sufficiency", check_co_design_iteration_sufficiency),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
