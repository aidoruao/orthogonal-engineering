# pr46_agape_witness/integration/pr40_witness_extension.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Extends PR #40's AGENT_FEED.md witness ledger with PR #46 entries.
# All entries are deterministic and byte-to-byte hashable.
# This module produces the row content; actual file writes are out of scope
# (handled by CI or external tooling) to keep the module pure/testable.

from __future__ import annotations

import hashlib
from typing import Any, Dict

from pr46_agape_witness.util.canonical import canonical_bytes
from pr46_agape_witness.util.hashing import sha256_hash


# Column names matching AGENT_FEED.md
FEED_COLUMNS = [
    "timestamp",
    "event_type",
    "agent_id",
    "event_hash",
    "prev_entry_hash",
    "entry_hash",
]


def make_feed_entry(
    timestamp: str,
    event_type: str,
    agent_id: str,
    event_hash: str,
    prev_entry_hash: str,
) -> Dict[str, str]:
    """
    Produce a deterministic AGENT_FEED.md-style row for a PR #46 event.

    Parameters:
      timestamp       — ISO-8601 timestamp (injected).
      event_type      — one of: grace_period, partial_compliance, forgiveness,
                        fork_healing, intent.
      agent_id        — the affected agent.
      event_hash      — SHA-256 hash of the specific event record.
      prev_entry_hash — hash of the previous AGENT_FEED entry (chain link).

    Returns a dict with all FEED_COLUMNS populated.
    """
    entry_doc = {
        "agent_id": agent_id,
        "event_hash": event_hash,
        "event_type": event_type,
        "prev_entry_hash": prev_entry_hash,
        "timestamp": timestamp,
    }
    entry_hash = sha256_hash(entry_doc)
    return {
        "timestamp": timestamp,
        "event_type": event_type,
        "agent_id": agent_id,
        "event_hash": event_hash,
        "prev_entry_hash": prev_entry_hash,
        "entry_hash": entry_hash,
    }


def format_feed_row(entry: Dict[str, str]) -> str:
    """Format a feed entry dict as a Markdown table row (pipe-delimited)."""
    values = [entry.get(col, "") for col in FEED_COLUMNS]
    return "| " + " | ".join(values) + " |"


def format_feed_header() -> str:
    """Return the Markdown table header for PR #46 AGENT_FEED extension."""
    header = "| " + " | ".join(FEED_COLUMNS) + " |"
    separator = "| " + " | ".join(["---"] * len(FEED_COLUMNS)) + " |"
    return header + "\n" + separator
