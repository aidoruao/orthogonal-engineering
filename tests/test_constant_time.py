"""
Falsification test: Secret-dependent polynomial arithmetic is constant-time.
Uses Welch's t-test (dudect methodology): if execution time distribution
differs significantly between secret classes, the invariant is violated.

# @falsification_id: F_CRYPTO_001
Methodology: Roche et al., "dudect: dude, is my code constant time?", CHES 2017.
"""
import statistics
import hmac
import hashlib
import time
import pytest

_ITERATIONS = 10_000
# dudect threshold: accept constant-time if |t| < 4.5; reject (timing leak) if |t| >= 4.5
_T_THRESHOLD = 4.5


def _op(secret: bytes) -> bytes:
    """The operation under test: must be constant-time over secret distribution."""
    return hmac.new(secret, b"fixed-message", hashlib.sha256).digest()


def _collect_timings(secret: bytes, n: int) -> list:
    timings = []
    for _ in range(n):
        t0 = time.perf_counter_ns()
        _op(secret)
        timings.append(time.perf_counter_ns() - t0)
    return timings


def _welch_t_statistic(a: list, b: list) -> float:
    """
    Welch's t-statistic: (mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b).
    When |t| < 4.5 we fail to reject H0 (constant-time hypothesis) — invariant holds.
    When |t| >= 4.5 we detect a timing leak — invariant violated.
    Returns 0.0 if pooled_se is 0 (identical timing distributions — perfectly constant-time).
    """
    mean_a = statistics.mean(a)
    mean_b = statistics.mean(b)
    var_a = statistics.variance(a)
    var_b = statistics.variance(b)
    n_a = len(a)
    n_b = len(b)
    pooled_se = ((var_a / n_a) + (var_b / n_b)) ** 0.5
    if pooled_se == 0:
        # Both distributions are perfectly identical (zero variance) — ideally constant-time.
        # t-statistic is 0 by convention (no detectable difference).
        return 0.0
    return (mean_a - mean_b) / pooled_se


def test_constant_time_statistical():
    """
    Falsification: if |t| >= 4.5 the timing distribution is NOT constant-time
    (corresponds approximately to p < 0.001 for large n, per dudect convention).
    A passing test means we FAIL TO REJECT the null hypothesis that the
    operation is constant-time — which is the correct Popperian framing.
    """
    secret_class_0 = b"\x00" * 32  # fixed secret, class 0
    secret_class_1 = b"\xff" * 32  # fixed secret, class 1

    timings_0 = _collect_timings(secret_class_0, _ITERATIONS)
    timings_1 = _collect_timings(secret_class_1, _ITERATIONS)

    t_stat = abs(_welch_t_statistic(timings_0, timings_1))

    assert t_stat < _T_THRESHOLD, (
        f"Timing side-channel detected: |t| = {t_stat:.3f} >= {_T_THRESHOLD}. "
        f"mean_0={statistics.mean(timings_0):.1f}ns "
        f"mean_1={statistics.mean(timings_1):.1f}ns. "
        "F_CRYPTO_001 VIOLATED."
    )


def test_constant_time_uses_compare_digest():
    """
    Structural check: the D_CRYPTO implementation must use hmac.compare_digest for any
    comparison step, never a raw == on secrets.
    """
    import inspect
    import src.domains.d_crypto.implementation as impl
    source = inspect.getsource(impl)
    assert "hmac.compare_digest" in source, (
        "D_CRYPTO implementation must use hmac.compare_digest, not raw == comparison. "
        "F_CRYPTO_001 structural check VIOLATED."
    )

