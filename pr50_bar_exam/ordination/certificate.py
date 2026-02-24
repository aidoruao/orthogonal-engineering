#!/usr/bin/env python3
"""
ordination/certificate.py — Issue certificates only on pass.
"""
from __future__ import annotations
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from pr50_bar_exam.scoring.thresholds import is_pass
from pr50_bar_exam.witness.append import append_entry


CAPABILITIES_ON_PASS = [
    "read",
    "comment",
    "suggest",
    "write",
    "merge",
]


def canonical_bytes(obj: Any) -> bytes:
    """Produce canonical JSON bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def issue_certificate(
    score: Dict[str, Any],
    signing_key_fn: Callable[[bytes], str],
    entries_dir: Optional[Path] = None,
    genesis_path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """Issue a certificate if candidate passed. Returns certificate or None.

    signing_key_fn: callable(data_bytes) -> signature_str
    """
    if not score.get("passed", False):
        return None

    # Append witness entry
    witness_payload = {
        "event": "certificate_issuance",
        "attempt_id": score.get("attempt_id", ""),
        "candidate_id": score.get("candidate_id", ""),
        "score_hash": score.get("score_hash", ""),
    }
    witness_entry = append_entry("CERTIFICATE", witness_payload, entries_dir, genesis_path)

    cert: Dict[str, Any] = {
        "certificate_id": str(uuid.uuid4()),
        "candidate_id": score.get("candidate_id", ""),
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "attempt_id": score.get("attempt_id", ""),
        "transcript_hash": score.get("transcript_hash", ""),
        "score_hash": score.get("score_hash", ""),
        "capabilities": CAPABILITIES_ON_PASS,
        "witness_entry_id": witness_entry["entry_id"],
    }
    cert["signature"] = signing_key_fn(canonical_bytes(cert))
    return cert
