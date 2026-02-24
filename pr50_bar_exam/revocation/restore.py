#!/usr/bin/env python3
"""
revocation/restore.py — Create witnessed restoration events.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pr50_bar_exam.revocation.authority import can_restore, load_authority_config
from pr50_bar_exam.revocation.effects import apply_restoration_effects
from pr50_bar_exam.witness.append import append_entry


def create_restoration_event(
    certificate: Dict[str, Any],
    authority_id: str,
    justification: str,
    authority_config: Optional[Dict] = None,
    entries_dir: Optional[Path] = None,
    genesis_path: Optional[Path] = None,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """Create a witnessed restoration event. Returns (event, errors)."""
    config = authority_config or load_authority_config()
    errors: List[str] = []

    if not can_restore(authority_id, config):
        errors.append(f"{authority_id!r} is not an authorized restoration authority")

    if errors:
        return None, errors

    restored_caps = apply_restoration_effects(certificate.get("capabilities", []))

    witness_payload = {
        "event": "restoration",
        "certificate_id": certificate.get("certificate_id", ""),
        "candidate_id": certificate.get("candidate_id", ""),
        "authority_id": authority_id,
    }
    witness_entry = append_entry("RESTORATION", witness_payload, entries_dir, genesis_path)

    event: Dict[str, Any] = {
        "event_id": str(uuid.uuid4()),
        "event_type": "RESTORATION",
        "certificate_id": certificate.get("certificate_id", ""),
        "candidate_id": certificate.get("candidate_id", ""),
        "authority_id": authority_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "trigger": "RESTORATION",
        "evidence": {"justification": justification},
        "witness_entry_id": witness_entry["entry_id"],
        "effects": restored_caps,
    }
    return event, []
