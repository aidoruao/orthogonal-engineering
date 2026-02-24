# pr47_stewardship/movement/boundary_encryptor.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# BoundaryEncryptor: deterministic XOR-based envelope for sensitive artifacts.
#
# Design:
#   - The key is injected (never derived from system state) for determinism.
#   - Encryption is symmetric: encrypt(encrypt(data, key), key) == data.
#   - The keystream is derived using HMAC-SHA256 in counter mode to avoid
#     length-extension vulnerabilities present in bare SHA-256 concatenation.
#   - This module provides a simple, auditable primitive; production deployments
#     should layer a proper KDF (e.g. HKDF) and authenticated encryption on top.

from __future__ import annotations

import hashlib
import hmac


def _derive_keystream(key: bytes, length: int) -> bytes:
    """
    Produce a deterministic keystream of `length` bytes from `key`.

    Uses HMAC-SHA256 in counter mode so the output is fully reproducible
    and avoids length-extension attacks.
    """
    stream = bytearray()
    counter = 0
    while len(stream) < length:
        block = hmac.new(key, counter.to_bytes(8, "big"), hashlib.sha256).digest()
        stream.extend(block)
        counter += 1
    return bytes(stream[:length])


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """
    XOR plaintext with a deterministic keystream derived from key.

    encrypt(encrypt(data, key), key) == data  (self-inverse).
    """
    keystream = _derive_keystream(key, len(plaintext))
    return bytes(p ^ k for p, k in zip(plaintext, keystream))


# encrypt and decrypt are identical for XOR, but both names are exported
# to make the intent explicit at call sites.
decrypt = encrypt
