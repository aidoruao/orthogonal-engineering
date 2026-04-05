"""F_CRYPTO_001 — constant-time statistical test (Welch t-test)."""

import statistics
import time

from src.domains.d_crypto.implementation import constant_time_hmac

_ITERATIONS = 10_000
_T_THRESHOLD = 4.5


def _collect(secret: bytes, n: int) -> list[int]:
    out = []
    for _ in range(n):
        t0 = time.perf_counter_ns()
        constant_time_hmac(secret, b"fixed-message")
        out.append(time.perf_counter_ns() - t0)
    return out


def _welch_t(a: list[int], b: list[int]) -> float:
    mean_a = statistics.mean(a)
    mean_b = statistics.mean(b)
    var_a = statistics.variance(a)
    var_b = statistics.variance(b)
    se = ((var_a / len(a)) + (var_b / len(b))) ** 0.5
    if se == 0:
        return 0.0
    return (mean_a - mean_b) / se


def test_constant_time_hmac_welch_t():
    c0 = _collect(b"\x00" * 32, _ITERATIONS)
    c1 = _collect(b"\xff" * 32, _ITERATIONS)
    t = abs(_welch_t(c0, c1))
    assert t < _T_THRESHOLD
    assert statistics.mean(c0) > 0
    assert statistics.mean(c1) > 0
    assert len(c0) == _ITERATIONS
    assert len(c1) == _ITERATIONS
    assert min(c0) >= 0
    assert min(c1) >= 0
    assert max(c0) >= min(c0)
    assert max(c1) >= min(c1)
    assert isinstance(t, float)
