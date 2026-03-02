"""
Falsification test: Signature verification rejects tampered messages.
Bit flip in message causes signature to fail.

# @falsification_id: F-CRYPTO-004
"""
import hmac
import hashlib
import pytest

KEY = b"signing_key_secret"

def sign(message: bytes) -> bytes:
    return hmac.new(KEY, message, hashlib.sha256).digest()

def verify(message: bytes, sig: bytes) -> bool:
    expected = sign(message)
    return hmac.compare_digest(expected, sig)

def test_tampered_message_rejected():
    message = b"authorize_payment_1000"
    sig = sign(message)
    tampered = bytearray(message)
    tampered[0] ^= 0x01
    assert not verify(bytes(tampered), sig), "Tampered message should fail verification"

def test_valid_message_accepted():
    message = b"authorize_payment_1000"
    sig = sign(message)
    assert verify(message, sig), "Valid message should pass verification"
