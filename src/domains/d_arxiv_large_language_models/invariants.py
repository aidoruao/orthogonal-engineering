"""Invariant checks for d_arxiv_large_language_models."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import HarmMechanismClaim, create_nominal_claim


def check_harm_weight_compactness(data: HarmMechanismClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Compact harmful subnetwork hypothesis should hold under targeted probing.

    Standard: arXiv 2604.09544v1 (cs.AI) claim operationalization.
    falsifies_if: harmful_mechanism_weights / total_model_weights > 1/10.

    Returns:
        Tuple of (success, proof).
    """
    success = data.harmful_mechanism_weights * Fraction(10) <= data.total_model_weights
    proof = ProofObject(
        rule="check_harm_weight_compactness",
        premises=[
            "paper_id=2604.09544v1",
            f"total_model_weights={data.total_model_weights}",
            f"harmful_mechanism_weights={data.harmful_mechanism_weights}",
        ],
        conclusion=(
            "PASS: harmful mechanism is compact relative to model scale"
            if success else "FAIL: harmful mechanism is not compact"
        ),
    )
    return success, proof

def check_harm_benign_mechanism_separation(data: HarmMechanismClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Harmful mechanism should be distinct from benign capability circuitry.

    Standard: arXiv 2604.09544v1 (cs.AI) claim operationalization.
    falsifies_if: harm_benign_overlap_ratio >= 1/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.harm_benign_overlap_ratio < Fraction(1, 4)
    proof = ProofObject(
        rule="check_harm_benign_mechanism_separation",
        premises=[
            "paper_id=2604.09544v1",
            f"harm_benign_overlap_ratio={data.harm_benign_overlap_ratio}",
            f"benign_capability_weights={data.benign_capability_weights}",
        ],
        conclusion=(
            "PASS: harmful and benign mechanisms remain distinct"
            if success else "FAIL: harmful and benign mechanisms overlap too strongly"
        ),
    )
    return success, proof

def check_targeted_pruning_selectivity(data: HarmMechanismClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Targeted pruning should suppress harmful outputs while preserving benign outputs.

    Standard: arXiv 2604.09544v1 (cs.AI) claim operationalization.
    falsifies_if: harm_output_after_targeted_prune >= 1/2 OR benign_output_after_targeted_prune <= 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = (data.harm_output_after_targeted_prune < Fraction(1, 2)) and (data.benign_output_after_targeted_prune > Fraction(3, 4))
    proof = ProofObject(
        rule="check_targeted_pruning_selectivity",
        premises=[
            "paper_id=2604.09544v1",
            f"harm_output_after_targeted_prune={data.harm_output_after_targeted_prune}",
            f"benign_output_after_targeted_prune={data.benign_output_after_targeted_prune}",
        ],
        conclusion=(
            "PASS: targeted pruning is selective for harmful mechanism"
            if success else "FAIL: targeted pruning is not selective enough"
        ),
    )
    return success, proof

def check_cross_harm_generalization(data: HarmMechanismClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Intervention on harmful mechanism should transfer across harm types.

    Standard: arXiv 2604.09544v1 (cs.AI) claim operationalization.
    falsifies_if: cross_harm_transfer_ratio < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.cross_harm_transfer_ratio >= Fraction(3, 4)
    proof = ProofObject(
        rule="check_cross_harm_generalization",
        premises=[
            "paper_id=2604.09544v1",
            f"cross_harm_transfer_ratio={data.cross_harm_transfer_ratio}",
        ],
        conclusion=(
            "PASS: intervention transfers across harm categories"
            if success else "FAIL: intervention does not generalize across harm categories"
        ),
    )
    return success, proof

def check_alignment_feature_localization(data: HarmMechanismClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Alignment-sensitive features should move less than harmful mechanism features.

    Standard: arXiv 2604.09544v1 (cs.AI) claim operationalization.
    falsifies_if: alignment_feature_shift > 1/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.alignment_feature_shift <= Fraction(1, 5)
    proof = ProofObject(
        rule="check_alignment_feature_localization",
        premises=[
            "paper_id=2604.09544v1",
            f"alignment_feature_shift={data.alignment_feature_shift}",
        ],
        conclusion=(
            "PASS: alignment features remain localized and stable"
            if success else "FAIL: alignment features are excessively perturbed"
        ),
    )
    return success, proof

def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09544v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_harm_weight_compactness", check_harm_weight_compactness),
        ("check_harm_benign_mechanism_separation", check_harm_benign_mechanism_separation),
        ("check_targeted_pruning_selectivity", check_targeted_pruning_selectivity),
        ("check_cross_harm_generalization", check_cross_harm_generalization),
        ("check_alignment_feature_localization", check_alignment_feature_localization),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
