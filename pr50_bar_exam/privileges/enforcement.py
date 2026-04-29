#!/usr/bin/env python3
"""
privileges/enforcement.py — Given a certificate and an action, decide if allowed.
"""
from __future__ import annotations
import fnmatch
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

MATRIX_PATH = Path(__file__).parent / "capability_matrix.json"


def load_capability_matrix() -> Dict[str, Any]:
    """Load the capability matrix."""
    # TODO: Expand load_capability_matrix() - stub detected by Yeshua Agent
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def get_capability_info(capability: str, matrix: Dict[str, Any]) -> Optional[Dict]:
    """Return capability info dict from matrix, or None."""
    for cap in matrix.get("capabilities", []):
        if cap["name"] == capability:
            return cap
    return None


def get_allowed_capabilities_for_path(path: str, matrix: Dict[str, Any]) -> List[str]:
    """Return capabilities allowed for path (most-specific scope wins)."""
    best_scope: Optional[Dict] = None
    best_len = -1
    for scope in matrix.get("path_scopes", []):
        pattern = scope["path_glob"]
        if fnmatch.fnmatch(path, pattern):
            if len(pattern) > best_len:
                best_len = len(pattern)
                best_scope = scope
    if best_scope is None:
        return ["read", "comment", "suggest"]
    return best_scope.get("allowed_capabilities", [])


def is_action_allowed(
    certificate: Dict[str, Any],
    action: str,
    path: str,
    consent_artifact: Optional[Dict] = None,
) -> Tuple[bool, str]:
    """Check if action on path is allowed given certificate and optional consent.

    Returns (allowed, reason).
    """
    if not certificate.get("capabilities"):
        return False, "certificate has no capabilities"

    matrix = load_capability_matrix()
    cap_info = get_capability_info(action, matrix)
    if cap_info is None:
        return False, f"unknown action: {action!r}"

    # Check certificate has the capability
    if action not in certificate.get("capabilities", []):
        return False, f"certificate does not grant {action!r}"

    # Check path scope
    allowed_caps = get_allowed_capabilities_for_path(path, matrix)
    if action not in allowed_caps:
        return False, f"{action!r} not allowed on path {path!r}"

    # Check consent requirement
    if cap_info.get("requires_consent"):
        if consent_artifact is None:
            return False, f"{action!r} requires consent artifact"
        from pr50_bar_exam.privileges.consent_bridge import validate_consent_artifact, consent_covers_action
        violations = validate_consent_artifact(consent_artifact)
        if violations:
            return False, f"invalid consent artifact: {violations}"
        if not consent_covers_action(consent_artifact, action, path):
            return False, f"consent artifact does not cover {action!r} on {path!r}"

    return True, "allowed"
