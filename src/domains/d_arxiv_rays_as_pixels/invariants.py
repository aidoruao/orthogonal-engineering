"""Invariant checks for d_arxiv_rays_as_pixels."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import RaysAsPixelsJointDistributionClaim, create_nominal_claim


def check_joint_pose_error_improvement(data: RaysAsPixelsJointDistributionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Joint video-camera modeling should reduce pose error under sparse coverage.

    Standard: arXiv 2604.09429v1 (cs.AI) claim operationalization.
    falsifies_if: joint_model_pose_error >= sparse_pose_error.

    Returns:
        Tuple of (success, proof).
    """
    success = data.joint_model_pose_error < data.sparse_pose_error
    proof = ProofObject(
        rule="check_joint_pose_error_improvement",
        premises=[
            "paper_id=2604.09429v1",
            f"sparse_pose_error={data.sparse_pose_error}",
            f"joint_model_pose_error={data.joint_model_pose_error}",
        ],
        conclusion=(
            "PASS: joint model improves pose estimation"
            if success else "FAIL: joint model does not improve pose estimation"
        ),
    )
    return success, proof

def check_novel_view_quality_floor(data: RaysAsPixelsJointDistributionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Novel-view rendering quality should exceed operational floor.

    Standard: arXiv 2604.09429v1 (cs.AI) claim operationalization.
    falsifies_if: novel_view_psnr < 4/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.novel_view_psnr >= Fraction(4, 5)
    proof = ProofObject(
        rule="check_novel_view_quality_floor",
        premises=[
            "paper_id=2604.09429v1",
            f"novel_view_psnr={data.novel_view_psnr}",
            f"ray_token_coverage={data.ray_token_coverage}",
        ],
        conclusion=(
            "PASS: novel-view quality floor is satisfied"
            if success else "FAIL: novel-view quality is insufficient"
        ),
    )
    return success, proof

def check_trajectory_cycle_consistency(data: RaysAsPixelsJointDistributionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Estimated camera trajectories should satisfy cycle consistency.

    Standard: arXiv 2604.09429v1 (cs.AI) claim operationalization.
    falsifies_if: trajectory_cycle_consistency < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.trajectory_cycle_consistency >= Fraction(3, 4)
    proof = ProofObject(
        rule="check_trajectory_cycle_consistency",
        premises=[
            "paper_id=2604.09429v1",
            f"trajectory_cycle_consistency={data.trajectory_cycle_consistency}",
            f"camera_path_smoothness={data.camera_path_smoothness}",
        ],
        conclusion=(
            "PASS: trajectory cycle consistency is strong"
            if success else "FAIL: trajectory cycle consistency is weak"
        ),
    )
    return success, proof

def check_ray_token_coverage_floor(data: RaysAsPixelsJointDistributionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Dense ray-token representation should maintain high scene coverage.

    Standard: arXiv 2604.09429v1 (cs.AI) claim operationalization.
    falsifies_if: ray_token_coverage < 4/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.ray_token_coverage >= Fraction(4, 5)
    proof = ProofObject(
        rule="check_ray_token_coverage_floor",
        premises=[
            "paper_id=2604.09429v1",
            f"ray_token_coverage={data.ray_token_coverage}",
        ],
        conclusion=(
            "PASS: ray-token coverage is sufficient"
            if success else "FAIL: ray-token coverage is insufficient"
        ),
    )
    return success, proof

def check_joint_distribution_gain(data: RaysAsPixelsJointDistributionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Joint video-camera likelihood should improve relative to decoupled baseline.

    Standard: arXiv 2604.09429v1 (cs.AI) claim operationalization.
    falsifies_if: joint_likelihood_gain <= 0 OR view_synthesis_temporal_consistency < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = (data.joint_likelihood_gain > Fraction(0)) and (data.view_synthesis_temporal_consistency >= Fraction(3, 4))
    proof = ProofObject(
        rule="check_joint_distribution_gain",
        premises=[
            "paper_id=2604.09429v1",
            f"joint_likelihood_gain={data.joint_likelihood_gain}",
            f"view_synthesis_temporal_consistency={data.view_synthesis_temporal_consistency}",
        ],
        conclusion=(
            "PASS: joint distribution learning provides measurable gain"
            if success else "FAIL: joint distribution gain is not demonstrated"
        ),
    )
    return success, proof

def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09429v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_joint_pose_error_improvement", check_joint_pose_error_improvement),
        ("check_novel_view_quality_floor", check_novel_view_quality_floor),
        ("check_trajectory_cycle_consistency", check_trajectory_cycle_consistency),
        ("check_ray_token_coverage_floor", check_ray_token_coverage_floor),
        ("check_joint_distribution_gain", check_joint_distribution_gain),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
