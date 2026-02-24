#!/usr/bin/env python3
"""
invariants/no_retake_without_period.py — Cooldown binding to GitHub actor + optional pubkey + sponsor.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_COOLDOWN_DAYS = 30


def check_retake_allowed(
    candidate_id: str,
    previous_attempts: List[Dict[str, Any]],
    cooldown_days: int = DEFAULT_COOLDOWN_DAYS,
    pubkey: Optional[str] = None,
    sponsor_id: Optional[str] = None,
) -> Tuple[bool, str]:
    """Check if candidate is allowed to retake the exam.

    Returns (allowed, reason).
    Binding: candidate_id (GitHub actor) + optional pubkey + optional sponsor.
    """
    now = datetime.now(timezone.utc)
    cooldown = timedelta(days=cooldown_days)

    relevant = [
        a for a in previous_attempts
        if a.get("candidate_id") == candidate_id
    ]
    if pubkey:
        relevant = [a for a in relevant if a.get("pubkey") == pubkey]
    if sponsor_id:
        relevant = [a for a in relevant if a.get("sponsor_id") == sponsor_id]

    if not relevant:
        return True, "no previous attempts found"

    def parse_ts(a: Dict) -> datetime:
        ts = a.get("timestamp_utc", "")
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    latest = max(relevant, key=parse_ts)
    latest_ts = parse_ts(latest)
    if latest_ts.tzinfo is None:
        latest_ts = latest_ts.replace(tzinfo=timezone.utc)

    elapsed = now - latest_ts
    if elapsed < cooldown:
        remaining = cooldown - elapsed
        return False, f"cooldown active: {remaining.days}d remaining"

    return True, "cooldown period elapsed"
