# pr46_agape_witness/grace/partial_compliance.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Partial compliance: agents that do not yet meet all requirements but are
# on an improving trajectory are accommodated, not excluded.

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pr46_agape_witness.grace.progress_trajectory import (
    TrajectoryDirection,
    classify_trajectory,
)
from pr46_agape_witness.law.compliance_registry import ComplianceStatus
from pr46_agape_witness.util.hashing import sha256_hash


@dataclass(frozen=True)
class PartialComplianceResult:
    """Result of a partial compliance determination."""
    agent_id: str
    scores: List[int]
    trajectory: TrajectoryDirection
    status: ComplianceStatus
    result_hash: str


def determine_partial_compliance(
    agent_id: str,
    scores: List[int],
    full_threshold: int,
) -> PartialComplianceResult:
    """
    Determine the compliance status of agent_id from their score trajectory.

    Rules:
      - If the most recent score >= full_threshold: FULL compliance.
      - If the trajectory is IMPROVING (regardless of threshold): PARTIAL.
        (NeverExclude: improving agents are never marked NON_COMPLIANT.)
      - Otherwise: NON_COMPLIANT.

    Parameters:
      agent_id        — identifier of the agent being evaluated.
      scores          — ordered list of integer compliance scores (most recent last).
      full_threshold  — minimum score for FULL compliance.

    Returns a PartialComplianceResult with a deterministic result_hash.
    Raises ValueError if scores is empty.
    """
    if not scores:
        raise ValueError("determine_partial_compliance requires at least one score")

    trajectory = classify_trajectory(scores)
    latest = scores[-1]

    if latest >= full_threshold:
        status = ComplianceStatus.FULL
    elif trajectory == TrajectoryDirection.IMPROVING:
        status = ComplianceStatus.PARTIAL
    else:
        status = ComplianceStatus.NON_COMPLIANT

    result_hash = sha256_hash({
        "agent_id": agent_id,
        "full_threshold": full_threshold,
        "scores": scores,
        "status": status.value,
        "trajectory": trajectory.value,
    })

    return PartialComplianceResult(
        agent_id=agent_id,
        scores=scores,
        trajectory=trajectory,
        status=status,
        result_hash=result_hash,
    )
