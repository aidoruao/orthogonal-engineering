#!/usr/bin/env python3
"""
candidate/sponsor.py — Sponsor approval policy (config-driven).

Sponsors are authorised third parties who vouch for a candidate.
Enforcement is optional and config-driven.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_POLICY: Dict[str, Any] = {
    "require_sponsor": False,
    "allowed_sponsors": [],
    "max_sponsors_required": 1,
}


def load_policy(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load sponsor policy from config file, falling back to defaults."""
    if config_path is not None and config_path.exists():
        data = json.loads(config_path.read_text(encoding="utf-8"))
        policy = {**DEFAULT_POLICY, **data}
    else:
        policy = dict(DEFAULT_POLICY)
    return policy


def is_sponsor_required(policy: Dict[str, Any]) -> bool:
    """Return True if sponsor approval is required."""
    return bool(policy.get("require_sponsor", False))


def is_approved_sponsor(sponsor_id: str, policy: Dict[str, Any]) -> bool:
    """Return True if sponsor_id is in the allowed sponsors list.

    If allowed_sponsors is empty and require_sponsor is False, always returns True.
    """
    allowed = policy.get("allowed_sponsors", [])
    if not allowed:
        return not is_sponsor_required(policy)
    return sponsor_id in allowed


def validate_sponsor(sponsor_id: Optional[str], policy: Dict[str, Any]) -> List[str]:
    """Validate sponsor against policy. Returns list of violation strings (empty = ok)."""
    violations: List[str] = []
    if is_sponsor_required(policy):
        if sponsor_id is None or not sponsor_id.strip():
            violations.append("sponsor_required: no sponsor_id provided")
        elif not is_approved_sponsor(sponsor_id, policy):
            violations.append(f"sponsor_not_allowed: {sponsor_id!r} not in allowed_sponsors")
    return violations
