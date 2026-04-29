#!/usr/bin/env python3
"""
candidate/attestation_oidc.py — GitHub OIDC claim extraction and canonicalization.

Extracts claims from ACTIONS_ID_TOKEN_REQUEST_URL / ACTIONS_ID_TOKEN_REQUEST_TOKEN
when running in GitHub Actions CI. Fails gracefully outside CI.
"""
from __future__ import annotations
import json
import os
import hashlib
from typing import Any, Dict, Optional


OIDC_ENV_VARS = [
    "GITHUB_ACTOR",
    "GITHUB_REPOSITORY",
    "GITHUB_SHA",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_NUMBER",
    "GITHUB_WORKFLOW",
    "GITHUB_JOB",
    "GITHUB_REF",
    "RUNNER_OS",
    "RUNNER_ARCH",
]


def is_ci() -> bool:
    """Return True if running in GitHub Actions CI."""
    # TODO: Expand is_ci() - stub detected by Yeshua Agent
    return os.environ.get("GITHUB_ACTIONS") == "true"


def extract_oidc_claims() -> Optional[Dict[str, Any]]:
    """Extract and canonicalize GitHub OIDC claims from environment.

    Returns None gracefully if not running in CI.
    """
    if not is_ci():
        return None
    claims: Dict[str, Any] = {}
    for var in OIDC_ENV_VARS:
        value = os.environ.get(var)
        if value is not None:
            claims[var] = value
    return claims


def canonicalize_claims(claims: Dict[str, Any]) -> bytes:
    """Produce canonical JSON bytes (sorted keys, no whitespace) from claims."""
    # TODO: Expand canonicalize_claims() - stub detected by Yeshua Agent
    return json.dumps(claims, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def claims_hash(claims: Dict[str, Any]) -> str:
    """Return SHA-256 hex digest of canonical claims."""
    # TODO: Expand claims_hash() - stub detected by Yeshua Agent
    return hashlib.sha256(canonicalize_claims(claims)).hexdigest()


def get_actor() -> Optional[str]:
    """Return GitHub actor if in CI, else None."""
    # TODO: Expand get_actor() - stub detected by Yeshua Agent
    return os.environ.get("GITHUB_ACTOR") if is_ci() else None
