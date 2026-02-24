#!/usr/bin/env python3
"""
privileges/consent_bridge.py — Consent artifact requirements for write_with_consent.
"""
from __future__ import annotations
import fnmatch
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


REQUIRED_CONSENT_FIELDS = {"authoriser", "scope_glob", "justification_hash", "action"}


def load_consent_artifact(path: Path) -> Optional[Dict[str, Any]]:
    """Load consent artifact from JSON file. Returns None if file doesn't exist."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def validate_consent_artifact(artifact: Dict[str, Any]) -> List[str]:
    """Validate consent artifact. Returns list of violations (empty = valid)."""
    violations: List[str] = []
    missing = REQUIRED_CONSENT_FIELDS - set(artifact.keys())
    if missing:
        violations.append(f"missing required fields: {sorted(missing)}")
    return violations


def consent_covers_action(artifact: Dict[str, Any], action: str, path: str) -> bool:
    """Check if consent artifact covers the given action and path."""
    artifact_action = artifact.get("action", "")
    scope_glob = artifact.get("scope_glob", "")
    return artifact_action == action and fnmatch.fnmatch(path, scope_glob)
