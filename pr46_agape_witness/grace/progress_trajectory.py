"""Progress Trajectory - pr46_agape_witness/grace/progress_trajectory.py"""
# pr46_agape_witness/grace/progress_trajectory.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Trajectory-based accommodation: agents showing improvement are never
# marked invalid, even if not yet fully compliant.

from __future__ import annotations

from enum import Enum
from typing import List


class TrajectoryDirection(Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


def classify_trajectory(scores: List[int]) -> TrajectoryDirection:
    """
    Classify an agent's compliance trajectory from an ordered list of
    integer compliance scores (higher = more compliant).

    Rules:
      - If the last score > the first score: IMPROVING.
      - If the last score < the first score: DECLINING.
      - Otherwise: STABLE.

    Deterministic: no randomness, no system clock.

    Raises ValueError if scores is empty.
    """
    if not scores:
        raise ValueError("classify_trajectory requires at least one score")
    if len(scores) == 1:
        return TrajectoryDirection.STABLE
    if scores[-1] > scores[0]:
        return TrajectoryDirection.IMPROVING
    if scores[-1] < scores[0]:
        return TrajectoryDirection.DECLINING
    return TrajectoryDirection.STABLE


def is_improving(scores: List[int]) -> bool:
    """Return True iff the trajectory is IMPROVING."""
    # TODO: Expand is_improving() - stub detected by Yeshua Agent
    return classify_trajectory(scores) == TrajectoryDirection.IMPROVING


def never_mark_invalid_if_improving(scores: List[int]) -> bool:
    """
    NeverExclude sub-rule: an improving agent must not be marked invalid.
    Returns True (agent is protected) if trajectory is IMPROVING.
    Returns False (no automatic protection) otherwise.
    """
    if not scores:
        return False
    return is_improving(scores)
