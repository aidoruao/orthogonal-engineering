"""
Falsification test: KDF produces identical output for identical inputs.
HKDF with same inputs always gives same output.

# @falsification_id: F_CRYPTO_003
"""
import hashlib
import hmac
import pytest

def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    return hmac.new(salt, ikm, hashlib.sha256).digest()

def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    okm, t, i = b"", b"", 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
        i += 1
    return okm[:length]

SALT = b"test_salt"
IKM = b"input_key_material"
INFO = b"app_context"

def test_kdf_deterministic():
    results = set()
    for _ in range(100):
        prk = hkdf_extract(SALT, IKM)
        okm = hkdf_expand(prk, INFO, 32)
        results.add(okm)
    assert len(results) == 1, "KDF produced different outputs for identical inputs"
