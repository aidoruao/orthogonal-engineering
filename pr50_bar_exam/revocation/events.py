#!/usr/bin/env python3
"""
revocation/events.py — Create witnessed revocation events.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pr50_bar_exam.revocation.triggers import validate_trigger_evidence
from pr50_bar_exam.revocation.authority import can_revoke, load_authority_config
from pr50_bar_exam.revocation.effects import apply_revocation_effects, CAPABILITIES_REMOVED_ON_REVOCATION
from pr50_bar_exam.witness.append import append_entry


def create_revocation_event(
    certificate: Dict[str, Any],
    authority_id: str,
    trigger: str,
    evidence: Dict[str, Any],
    authority_config: Optional[Dict] = None,
    entries_dir: Optional[Path] = None,
    genesis_path: Optional[Path] = None,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """Create a witnessed revocation event. Returns (event, errors)."""
    config = authority_config or load_authority_config()
    errors: List[str] = []

    if not can_revoke(authority_id, config):
        errors.append(f"{authority_id!r} is not an authorized revocation authority")

    evidence_errors = validate_trigger_evidence(trigger, evidence)
    errors.extend(evidence_errors)

    if errors:
        return None, errors

    witness_payload = {
        "event": "revocation",
        "certificate_id": certificate.get("certificate_id", ""),
        "candidate_id": certificate.get("candidate_id", ""),
        "trigger": trigger,
        "authority_id": authority_id,
    }
    witness_entry = append_entry("REVOCATION", witness_payload, entries_dir, genesis_path)

    event: Dict[str, Any] = {
        "event_id": str(uuid.uuid4()),
        "event_type": "REVOCATION",
        "certificate_id": certificate.get("certificate_id", ""),
        "candidate_id": certificate.get("candidate_id", ""),
        "authority_id": authority_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "trigger": trigger,
        "evidence": evidence,
        "witness_entry_id": witness_entry["entry_id"],
        "effects": CAPABILITIES_REMOVED_ON_REVOCATION,
    }
    return event, []
