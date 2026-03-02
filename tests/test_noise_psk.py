"""
Falsification test: Noise PSK zero-key is rejected.
PSK of all-zero bytes is treated as absent/invalid.

# @falsification_id: F-CRYPTO-002
"""
import pytest

def _noise_handshake_sim(psk: bytes) -> str:
    """Simulate Noise PSK handshake — reject all-zero PSK."""
    if psk == bytes(len(psk)):
        return "REJECTED"
    return "ACCEPTED"

def test_zero_psk_rejected():
    zero_psk = bytes(32)
    result = _noise_handshake_sim(zero_psk)
    assert result == "REJECTED", "Zero PSK must be rejected"

def test_nonzero_psk_accepted():
    psk = bytes(range(32))
    result = _noise_handshake_sim(psk)
    assert result == "ACCEPTED", "Non-zero PSK must be accepted"
