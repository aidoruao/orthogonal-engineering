"""
Falsification test: Key generation is deterministic from seed.
Same seed -> same key pair.

# @falsification_id: F_CRYPTO_007
"""
import hashlib
import pytest

def derive_key(seed: bytes) -> bytes:
    return hashlib.sha256(b"key_derive:" + seed).digest()

SEED = b"fixed_test_seed_12345"

def test_key_derivation_deterministic():
    keys = [derive_key(SEED) for _ in range(100)]
    assert len(set(keys)) == 1, "Key derivation is not deterministic"
