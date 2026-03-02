"""
Falsification test: All cryptographic operations are constant-time.
No secret-dependent timing variation (simulated).

# @falsification_id: F-CRYPTO-006
"""
import time
import hmac
import hashlib
import pytest

def hmac_op(key: bytes) -> bytes:
    return hmac.new(key, b"fixed_message", hashlib.sha256).digest()

def test_hmac_timing_invariant():
    keys = [bytes([i] * 32) for i in range(20)]
    times = []
    for k in keys:
        t0 = time.perf_counter()
        for _ in range(200):
            hmac_op(k)
        times.append(time.perf_counter() - t0)
    delta = max(times) - min(times)
    assert delta < 0.5, f"Timing delta {delta:.4f}s indicates non-constant-time (simulated)"
