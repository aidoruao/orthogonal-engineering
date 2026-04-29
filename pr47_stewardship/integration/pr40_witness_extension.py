"""Pr40 Witness Extension - pr47_stewardship/integration/pr40_witness_extension.py"""
# pr47_stewardship/integration/pr40_witness_extension.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# Extends the PR #40 AGENT_FEED.md witness ledger with PR #47 boundary
# transition events.  Produces deterministic row content; actual file writes
# are out of scope (handled by CI or external tooling) to keep the module
# pure/testable.

from __future__ import annotations

import hashlib
import json
from typing import Dict, List


FEED_COLUMNS: List[str] = [
    "timestamp",
    "event_type",
    "content_hash",
    "reason_code",
    "consent_hash",
    "prev_entry_hash",
    "entry_hash",
]

# Stable event type for PR #47 boundary transition events.
EVENT_TYPE = "boundary_transition"


def _sha256(doc: dict) -> str:
    """Deterministic SHA-256 over a sorted-key JSON document."""
    raw = json.dumps(doc, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def make_feed_entry(
    timestamp: str,
    content_hash: str,
    reason_code: str,
    consent_hash: str,
    prev_entry_hash: str,
) -> Dict[str, str]:
    """
    Produce a deterministic AGENT_FEED.md-style row for a PR #47 event.

    Parameters:
      timestamp       — ISO-8601 timestamp (injected).
      content_hash    — SHA-256 of the transitioned artifact.
      reason_code     — opaque reason code (e.g. "R1").
      consent_hash    — SHA-256 of the authorising consent record.
      prev_entry_hash — hash of the previous AGENT_FEED entry (chain link).

    Returns a dict with all FEED_COLUMNS populated.
    """
    entry_doc = {
        "consent_hash": consent_hash,
        "content_hash": content_hash,
        "event_type": EVENT_TYPE,
        "prev_entry_hash": prev_entry_hash,
        "reason_code": reason_code,
        "timestamp": timestamp,
    }
    entry_hash = _sha256(entry_doc)
    return {
        "timestamp": timestamp,
        "event_type": EVENT_TYPE,
        "content_hash": content_hash,
        "reason_code": reason_code,
        "consent_hash": consent_hash,
        "prev_entry_hash": prev_entry_hash,
        "entry_hash": entry_hash,
    }


def format_feed_row(entry: Dict[str, str]) -> str:
    """Format a feed entry dict as a Markdown table row (pipe-delimited)."""
    values = [entry.get(col, "") for col in FEED_COLUMNS]
    return "| " + " | ".join(values) + " |"


def format_feed_header() -> str:
    """Return the Markdown table header for PR #47 AGENT_FEED extension."""
    header = "| " + " | ".join(FEED_COLUMNS) + " |"
    separator = "| " + " | ".join(["---"] * len(FEED_COLUMNS)) + " |"
    return header + "\n" + separator
