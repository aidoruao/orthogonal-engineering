#!/usr/bin/env python3
"""
ordination/signing_repo_key.py — Abstraction for signing using a repo key.

Supports dev/test key path for tests.
"""
from __future__ import annotations
import hashlib
import hmac
import os
from pathlib import Path
from typing import Callable, Optional


DEV_KEY_ENV = "PR50_SIGNING_KEY"
DEV_KEY_DEFAULT = "a" * 64  # Fallback 32-byte all-'a' key in hex (for tests only)


def get_signing_key() -> str:
    """Return signing key from environment or fall back to dev default."""
    return os.environ.get(DEV_KEY_ENV, DEV_KEY_DEFAULT)


def make_signing_fn(secret_key: Optional[str] = None) -> Callable[[bytes], str]:
    """Return a signing function that signs bytes and returns hex signature."""
    key = secret_key or get_signing_key()
    key_bytes = bytes.fromhex(key)

    def sign(data: bytes) -> str:
        mac = hmac.new(key_bytes, data, hashlib.sha256)
        return mac.hexdigest()

    return sign


def make_verify_fn(secret_key: Optional[str] = None) -> Callable[[bytes, str], bool]:
    """Return a verification function."""
    key = secret_key or get_signing_key()
    sign_fn = make_signing_fn(key)

    def verify(data: bytes, signature: str) -> bool:
        expected = sign_fn(data)
        return hmac.compare_digest(expected, signature)

    return verify
