"""Implementation models for d_arxiv_rays_as_pixels."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class RaysAsPixelsJointDistributionClaim:
    """Structured claim parameters derived from arXiv paper 2604.09429v1 (cs.AI)."""

    sparse_pose_error: Fraction
    joint_model_pose_error: Fraction
    novel_view_psnr: Fraction
    trajectory_cycle_consistency: Fraction
    ray_token_coverage: Fraction
    joint_likelihood_gain: Fraction
    view_synthesis_temporal_consistency: Fraction
    camera_path_smoothness: Fraction

def create_nominal_claim() -> RaysAsPixelsJointDistributionClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return RaysAsPixelsJointDistributionClaim(
        sparse_pose_error=Fraction(3, 10),
        joint_model_pose_error=Fraction(1, 5),
        novel_view_psnr=Fraction(17, 20),
        trajectory_cycle_consistency=Fraction(4, 5),
        ray_token_coverage=Fraction(9, 10),
        joint_likelihood_gain=Fraction(1, 8),
        view_synthesis_temporal_consistency=Fraction(4, 5),
        camera_path_smoothness=Fraction(3, 4),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_RAYS_AS_PIXELS",
    "paper_id": "2604.09429v1",
    "claim_model": "RaysAsPixelsJointDistributionClaim",
    "check_functions": [
        "check_joint_pose_error_improvement",
        "check_novel_view_quality_floor",
        "check_trajectory_cycle_consistency",
        "check_ray_token_coverage_floor",
        "check_joint_distribution_gain",
    ],
}
