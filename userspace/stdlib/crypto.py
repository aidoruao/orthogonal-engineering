#!/usr/bin/env python3
"""
Cryptographic library for userspace

SHA-256, HMAC, key derivation — all with ProofObjects.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import hashlib
import hmac

from axioms.logic import ProofObject
from axioms.cryptographic_verification import HashChain


def sha256(data: bytes) -> Tuple[str, ProofObject]:
    """Compute SHA-256 hash."""
    result = hashlib.sha256(data).hexdigest()
    
    return result, ProofObject(
        rule="SHA256",
        premises=[f"input_len={len(data)}"],
        conclusion=f"hash={result[:16]}..."
    )


def hmac_sha256(key: bytes, data: bytes) -> Tuple[str, ProofObject]:
    """Compute HMAC-SHA256."""
    result = hmac.new(key, data, hashlib.sha256).hexdigest()
    
    return result, ProofObject(
        rule="HMAC",
        premises=[f"key_len={len(key)}", f"data_len={len(data)}"],
        conclusion=f"hmac={result[:16]}..."
    )


def verify_hash(data: bytes, expected_hash: str) -> Tuple[bool, ProofObject]:
    """Verify data matches expected hash."""
    computed, _ = sha256(data)
    valid = computed == expected_hash
    
    return valid, ProofObject(
        rule="VerifyHash",
        premises=[f"expected={expected_hash[:16]}..."],
        conclusion=f"valid={valid}"
    )
