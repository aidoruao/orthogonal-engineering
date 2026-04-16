"""Invariant checks for d_arxiv_seeing_is_believing."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import VisionGuidedPromptRobustnessClaim, create_nominal_claim


def check_visual_signal_dominance(data: VisionGuidedPromptRobustnessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Visual semantics should remain more stable than prompt parameters under noise.

    Standard: arXiv 2604.09532v1 (cs.AI) claim operationalization.
    falsifies_if: visual_semantic_stability <= prompt_parameter_stability.

    Returns:
        Tuple of (success, proof).
    """
    success = data.visual_semantic_stability > data.prompt_parameter_stability
    proof = ProofObject(
        rule="check_visual_signal_dominance",
        premises=[
            "paper_id=2604.09532v1",
            f"visual_semantic_stability={data.visual_semantic_stability}",
            f"prompt_parameter_stability={data.prompt_parameter_stability}",
        ],
        conclusion=(
            "PASS: visual guidance dominates prompt fragility"
            if success else "FAIL: prompt instability overwhelms visual guidance"
        ),
    )
    return success, proof

def check_noise_reliance_bound(data: VisionGuidedPromptRobustnessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Model dependence on noisy labels should remain bounded.

    Standard: arXiv 2604.09532v1 (cs.AI) claim operationalization.
    falsifies_if: noisy_label_reliance > 1/3.

    Returns:
        Tuple of (success, proof).
    """
    success = data.noisy_label_reliance <= Fraction(1, 3)
    proof = ProofObject(
        rule="check_noise_reliance_bound",
        premises=[
            "paper_id=2604.09532v1",
            f"label_noise_rate={data.label_noise_rate}",
            f"noisy_label_reliance={data.noisy_label_reliance}",
        ],
        conclusion=(
            "PASS: noisy label reliance is controlled"
            if success else "FAIL: noisy label reliance is excessive"
        ),
    )
    return success, proof

def check_noisy_accuracy_floor(data: VisionGuidedPromptRobustnessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Noisy-label accuracy should remain above practical threshold.

    Standard: arXiv 2604.09532v1 (cs.AI) claim operationalization.
    falsifies_if: noisy_set_accuracy < 3/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.noisy_set_accuracy >= Fraction(3, 5)
    proof = ProofObject(
        rule="check_noisy_accuracy_floor",
        premises=[
            "paper_id=2604.09532v1",
            f"noisy_set_accuracy={data.noisy_set_accuracy}",
        ],
        conclusion=(
            "PASS: noisy-label performance remains acceptable"
            if success else "FAIL: noisy-label performance falls below floor"
        ),
    )
    return success, proof

def check_clean_noisy_gap_control(data: VisionGuidedPromptRobustnessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Generalization gap between clean and noisy sets should stay narrow.

    Standard: arXiv 2604.09532v1 (cs.AI) claim operationalization.
    falsifies_if: clean_set_accuracy - noisy_set_accuracy > 1/5.

    Returns:
        Tuple of (success, proof).
    """
    success = (data.clean_set_accuracy - data.noisy_set_accuracy) <= Fraction(1, 5)
    proof = ProofObject(
        rule="check_clean_noisy_gap_control",
        premises=[
            "paper_id=2604.09532v1",
            f"clean_set_accuracy={data.clean_set_accuracy}",
            f"noisy_set_accuracy={data.noisy_set_accuracy}",
            f"robustness_margin={data.robustness_margin}",
        ],
        conclusion=(
            "PASS: clean/noisy generalization gap is controlled"
            if success else "FAIL: clean/noisy gap indicates weak robustness"
        ),
    )
    return success, proof

def check_cross_modal_prompt_gain(data: VisionGuidedPromptRobustnessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Vision-guided cross-modal prompting should provide positive gain.

    Standard: arXiv 2604.09532v1 (cs.AI) claim operationalization.
    falsifies_if: cross_modal_alignment_gain <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.cross_modal_alignment_gain > Fraction(0)
    proof = ProofObject(
        rule="check_cross_modal_prompt_gain",
        premises=[
            "paper_id=2604.09532v1",
            f"cross_modal_alignment_gain={data.cross_modal_alignment_gain}",
            f"robustness_margin={data.robustness_margin}",
        ],
        conclusion=(
            "PASS: cross-modal guidance improves robust prompting"
            if success else "FAIL: no measured gain from cross-modal guidance"
        ),
    )
    return success, proof

def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09532v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_visual_signal_dominance", check_visual_signal_dominance),
        ("check_noise_reliance_bound", check_noise_reliance_bound),
        ("check_noisy_accuracy_floor", check_noisy_accuracy_floor),
        ("check_clean_noisy_gap_control", check_clean_noisy_gap_control),
        ("check_cross_modal_prompt_gain", check_cross_modal_prompt_gain),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
