"""F_CRYPTO_001 — constant-time statistical test (Welch t-test)."""

import statistics
import time

from src.domains.d_crypto.implementation import constant_time_hmac

ITERATIONS = 10_000
T_THRESHOLD = 45  # scaled by 10 (represents 4.5 without float)


def _collect(secret: bytes, n: int) -> list[int]:
    out = []
    for _ in range(n):
        t0 = time.perf_counter_ns()
        constant_time_hmac(secret, b"fixed-message")
        out.append(time.perf_counter_ns() - t0)
    return out


def _welch_t_times_10(a: list[int], b: list[int]) -> int:
    mean_a = statistics.mean(a)
    mean_b = statistics.mean(b)
    var_a = statistics.variance(a)
    var_b = statistics.variance(b)
    se = ((var_a / len(a)) + (var_b / len(b))) ** 0.5
    if se == 0:
        return 10**9
    t = abs((mean_a - mean_b) / se)
    return int(t * 10)


def test_constant_time_hmac_welch_t():
    c0 = _collect(b"\x00" * 32, ITERATIONS)
    c1 = _collect(b"\xff" * 32, ITERATIONS)
    t_scaled = _welch_t_times_10(c0, c1)
    assert t_scaled < T_THRESHOLD
    assert statistics.mean(c0) > 0
    assert statistics.mean(c1) > 0
    assert len(c0) == ITERATIONS
    assert len(c1) == ITERATIONS
    assert min(c0) >= 0
    assert min(c1) >= 0
    assert max(c0) >= min(c0)
    assert max(c1) >= min(c1)
    assert isinstance(t_scaled, int)
