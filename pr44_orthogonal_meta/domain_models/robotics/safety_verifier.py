# pr44_orthogonal_meta/domain_models/robotics/safety_verifier.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# Byte-verifiable collision avoidance for robotic systems.
# All safety proofs constructive; no probabilistic argumentation.
# Termination guaranteed: finite state space, structural recursion.

from __future__ import annotations

from typing import Dict, List, Set, Tuple

Pos = Tuple[int, int]


def verify_path_safe(path: List[Pos], obstacles: Set[Pos]) -> Dict:
    """
    Verify that no position in path coincides with any obstacle.

    Returns a proof record:
      - safe: bool
      - first_violation: Optional[Pos]
      - steps_checked: int
    """
    for i, pos in enumerate(path):
        if pos in obstacles:
            return {
                "theorem": "CollisionAvoidance",
                "safe": False,
                "first_violation": pos,
                "step_index": i,
                "steps_checked": i + 1,
            }
    return {
        "theorem": "CollisionAvoidance",
        "safe": True,
        "first_violation": None,
        "step_index": None,
        "steps_checked": len(path),
    }


def verify_bounded(path: List[Pos], max_coord: int) -> Dict:
    """
    Verify that all positions lie within [0, max_coord]².
    Constructive: checked step by step.
    """
    for i, (x, y) in enumerate(path):
        if x < 0 or y < 0 or x > max_coord or y > max_coord:
            return {
                "theorem": "BoundaryEnforcement",
                "within_bounds": False,
                "first_violation": (x, y),
                "step_index": i,
            }
    return {
        "theorem": "BoundaryEnforcement",
        "within_bounds": True,
        "first_violation": None,
        "steps_checked": len(path),
    }
