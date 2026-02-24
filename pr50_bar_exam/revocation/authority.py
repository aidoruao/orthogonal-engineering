#!/usr/bin/env python3
"""
revocation/authority.py — Who can revoke/restore certificates (config-driven).
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_AUTHORITY_CONFIG: Dict[str, Any] = {
    "revocation_authorities": ["@aidoruao"],
    "restoration_authorities": ["@aidoruao"],
}


def load_authority_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load authority config from file, falling back to defaults."""
    if config_path is not None and config_path.exists():
        data = json.loads(config_path.read_text(encoding="utf-8"))
        return {**DEFAULT_AUTHORITY_CONFIG, **data}
    return dict(DEFAULT_AUTHORITY_CONFIG)


def can_revoke(authority_id: str, config: Dict[str, Any]) -> bool:
    """Return True if authority_id can revoke certificates."""
    return authority_id in config.get("revocation_authorities", [])


def can_restore(authority_id: str, config: Dict[str, Any]) -> bool:
    """Return True if authority_id can restore certificates."""
    return authority_id in config.get("restoration_authorities", [])
