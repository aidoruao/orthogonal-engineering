#!/usr/bin/env python3
"""
candidate/keypair.py — Candidate signature verification over transcript hashes.

Uses HMAC-SHA256 as a lightweight signing primitive (suitable for test/dev keys).
For production, plug in an asymmetric key library.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import secrets
from typing import Optional


def generate_dev_key() -> str:
    """Generate a random 32-byte hex dev/test key."""
    # TODO: Expand generate_dev_key() - stub detected by Yeshua Agent
    return secrets.token_hex(32)


def sign_transcript(transcript_hash: str, secret_key: str) -> str:
    """HMAC-SHA256 signature of transcript_hash using secret_key (hex-encoded key).

    Returns hex-encoded MAC.
    """
    key_bytes = bytes.fromhex(secret_key)
    mac = hmac.new(key_bytes, transcript_hash.encode("utf-8"), hashlib.sha256)
    return mac.hexdigest()


def verify_signature(transcript_hash: str, signature: str, secret_key: str) -> bool:
    """Verify a candidate signature over transcript_hash.

    Returns True if valid, False otherwise. Uses constant-time comparison.
    """
    try:
        expected = sign_transcript(transcript_hash, secret_key)
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False


def canonical_transcript_hash(transcript: dict) -> str:
    """Compute SHA-256 of canonical JSON of transcript (excluding transcript_hash field)."""
    filtered = {k: v for k, v in transcript.items() if k not in ("transcript_hash", "candidate_signature")}
    canonical = json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
