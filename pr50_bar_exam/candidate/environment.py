#!/usr/bin/env python3
"""
candidate/environment.py — Deterministic environment capture and hashing.

Captures: runner version, promptset hash, scoring version, seed policy.
"""
from __future__ import annotations
import hashlib
import json
import platform
import sys
from typing import Any, Dict


SCORING_VERSION = "50.0.0"
SEED_POLICY = "fixed:42"  # Fixed seed for determinism


def capture_environment(promptset_hash: str) -> Dict[str, Any]:
    """Capture deterministic environment snapshot."""
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.system(),
        "scoring_version": SCORING_VERSION,
        "promptset_hash": promptset_hash,
        "seed_policy": SEED_POLICY,
    }


def canonicalize_environment(env: Dict[str, Any]) -> bytes:
    """Produce canonical JSON bytes of environment."""
    return json.dumps(env, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def environment_hash(env: Dict[str, Any]) -> str:
    """Return SHA-256 hex digest of environment."""
    return hashlib.sha256(canonicalize_environment(env)).hexdigest()
