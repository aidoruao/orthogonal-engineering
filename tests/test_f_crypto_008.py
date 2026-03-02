"""
Falsification test: Protocol implementations satisfy formal specification.
HMAC matches known test vectors from RFC 2104.

# @falsification_id: F-CRYPTO-008
"""
import hmac
import hashlib
import pytest

# RFC 2104 test vector (using MD5 for the original RFC, adapted for SHA-256 here)
# Using NIST HMAC-SHA-256 test vector
KEY = bytes.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")
DATA = b"Hi There"
EXPECTED = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"

def test_hmac_sha256_test_vector():
    result = hmac.new(KEY, DATA, hashlib.sha256).hexdigest()
    assert result == EXPECTED, f"HMAC-SHA256 mismatch: {result} != {EXPECTED}"
