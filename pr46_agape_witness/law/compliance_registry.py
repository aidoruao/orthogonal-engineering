# pr46_agape_witness/law/compliance_registry.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Compliance registry: tracks whether agents are in full, partial, or
# non-compliance, based on their observed trajectory.
# No agent is ever permanently marked invalid (NeverExclude invariant).

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from pr46_agape_witness.util.hashing import sha256_hash


class ComplianceStatus(Enum):
    FULL = "full"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    # An improving agent in a grace period is always PARTIAL, never excluded.


@dataclass(frozen=True)
class ComplianceRecord:
    """Immutable compliance record for one agent at one point in time."""
    agent_id: str
    status: ComplianceStatus
    basis: str          # human-readable reason
    trajectory: str     # "improving" | "stable" | "declining"
    timestamp: str      # ISO-8601 string (injected, not system clock)

    def record_hash(self) -> str:
        return sha256_hash({
            "agent_id": self.agent_id,
            "basis": self.basis,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "trajectory": self.trajectory,
        })


class ComplianceRegistry:
    """
    Append-only registry of compliance records per agent.
    History is never discarded (AlwaysRecoverable invariant).
    """

    def __init__(self) -> None:
        self._history: List[ComplianceRecord] = []

    def record(self, entry: ComplianceRecord) -> None:
        """Append a new compliance record (append-only)."""
        self._history.append(entry)

    def current_status(self, agent_id: str) -> Optional[ComplianceStatus]:
        """Return the most recent compliance status for agent_id, or None."""
        for entry in reversed(self._history):
            if entry.agent_id == agent_id:
                return entry.status
        return None

    def history_for(self, agent_id: str) -> List[ComplianceRecord]:
        """Return all records for agent_id in append order."""
        return [e for e in self._history if e.agent_id == agent_id]

    def all_records(self) -> List[ComplianceRecord]:
        """Return a copy of the entire history."""
        return list(self._history)
