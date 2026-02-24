# pr46_agape_witness/grace/grace_period.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Grace periods: time-bounded remediation windows.
# All time operations accept current_time as an injected parameter
# to keep tests and execution deterministic.

from __future__ import annotations

from dataclasses import dataclass

from pr46_agape_witness.util.hashing import sha256_hash


@dataclass(frozen=True)
class GracePeriod:
    """
    A witnessed, deterministic grace period for an agent.

    Fields:
      agent_id      — the agent receiving the grace period.
      start_time    — ISO-8601 string (injected, not system clock).
      duration_secs — length of the grace window in whole seconds.
      reason        — human-readable justification.
      witness_hash  — SHA-256 of the canonical grace period record.
    """
    agent_id: str
    start_time: str
    duration_secs: int
    reason: str
    witness_hash: str

    @classmethod
    def create(
        cls,
        agent_id: str,
        start_time: str,
        duration_secs: int,
        reason: str,
    ) -> "GracePeriod":
        """
        Factory: create a GracePeriod and compute its deterministic witness_hash.
        """
        doc = {
            "agent_id": agent_id,
            "duration_secs": duration_secs,
            "reason": reason,
            "start_time": start_time,
        }
        witness_hash = sha256_hash(doc)
        return cls(
            agent_id=agent_id,
            start_time=start_time,
            duration_secs=duration_secs,
            reason=reason,
            witness_hash=witness_hash,
        )

    def is_active(self, current_time_secs: int, start_epoch_secs: int) -> bool:
        """
        Return True iff the grace period is active at current_time_secs.

        Parameters:
          current_time_secs  — current time as integer seconds since epoch
                               (injected; deterministic).
          start_epoch_secs   — start_time expressed as integer seconds since epoch.
        """
        elapsed = current_time_secs - start_epoch_secs
        return 0 <= elapsed < self.duration_secs

    def remaining_secs(self, current_time_secs: int, start_epoch_secs: int) -> int:
        """
        Return seconds remaining in the grace period (0 if expired or not yet started).
        """
        elapsed = current_time_secs - start_epoch_secs
        remaining = self.duration_secs - elapsed
        return max(0, remaining)
