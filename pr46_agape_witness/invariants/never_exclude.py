# pr46_agape_witness/invariants/never_exclude.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# NeverExclude invariant: no agent may be permanently excluded.
# Every agent must always have a remediation path available.

from __future__ import annotations

from pr46_agape_witness.grace.progress_trajectory import classify_trajectory, TrajectoryDirection
from pr46_agape_witness.law.compliance_registry import ComplianceStatus


def check_never_exclude(
    agent_id: str,
    status: ComplianceStatus,
    scores: list,
) -> bool:
    """
    NeverExclude invariant: an agent that is improving must not be
    marked NON_COMPLIANT (which would imply permanent exclusion).

    Parameters:
      agent_id — identifier (used in error messages only).
      status   — the proposed ComplianceStatus.
      scores   — trajectory scores (used to check IMPROVING).

    Returns True if the invariant holds.
    Raises ValueError on violation.
    """
    if not scores:
        return True  # no data: vacuously satisfied
    trajectory = classify_trajectory(scores)
    if (
        trajectory == TrajectoryDirection.IMPROVING
        and status == ComplianceStatus.NON_COMPLIANT
    ):
        raise ValueError(
            f"NeverExclude invariant violated for agent {agent_id!r}: "
            f"improving trajectory must not be marked NON_COMPLIANT"
        )
    return True


def assert_remediation_path_exists(agent_id: str, has_grace_period: bool) -> bool:
    """
    Assert that a non-compliant agent has a remediation path (grace period).
    Raises ValueError if no remediation path exists.
    """
    if not has_grace_period:
        raise ValueError(
            f"NeverExclude: agent {agent_id!r} has no remediation path (no grace period)"
        )
    return True
