"""Covenant Tracking - pr46_agape_witness/relational/covenant_tracking.py"""
# pr46_agape_witness/relational/covenant_tracking.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Covenant tracking: append-only log of relational covenants
# (mutual agreements) between agents.

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pr46_agape_witness.util.hashing import sha256_hash


@dataclass(frozen=True)
class CovenantEntry:
    """An immutable record of a mutual covenant between two agents."""
    party_a: str
    party_b: str
    commitment: str     # human-readable commitment text
    timestamp: str      # ISO-8601, injected
    covenant_hash: str

    @classmethod
    def create(
        cls,
        party_a: str,
        party_b: str,
        commitment: str,
        timestamp: str,
    ) -> "CovenantEntry":
        doc = {
            "commitment": commitment,
            "party_a": sorted([party_a, party_b])[0],
            "party_b": sorted([party_a, party_b])[1],
            "timestamp": timestamp,
        }
        return cls(
            party_a=doc["party_a"],
            party_b=doc["party_b"],
            commitment=commitment,
            timestamp=timestamp,
            covenant_hash=sha256_hash(doc),
        )


class CovenantLog:
    """Append-only log of covenants."""

    def __init__(self) -> None:
        self._entries: List[CovenantEntry] = []

    def record(self, entry: CovenantEntry) -> None:
        self._entries.append(entry)

    def entries(self) -> List[CovenantEntry]:
        # TODO: Expand entries() - stub detected by Yeshua Agent
        return list(self._entries)
