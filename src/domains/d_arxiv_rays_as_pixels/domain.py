"""D_ARXIV_RAYS_AS_PIXELS domain definition — arXiv-derived executable invariants."""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARXIV_RAYS_AS_PIXELS"
DOMAIN_NAME = "Arxiv Rays As Pixels"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "arxiv",
    "cs.AI",
    "paper:2604.09429v1",
]

INVARIANTS = [
    "check_joint_pose_error_improvement",
    "check_novel_view_quality_floor",
    "check_trajectory_cycle_consistency",
    "check_ray_token_coverage_floor",
    "check_joint_distribution_gain",
]

FALSIFICATION_TESTS = ["F_D_ARXIV_RAYS_AS_PIXELS_001"]
ONTOLOGICAL_ISSUES = ["OI_D_ARXIV_RAYS_AS_PIXELS_001"]
