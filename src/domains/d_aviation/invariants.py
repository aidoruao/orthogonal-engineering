"""
D_AVIATION invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ontology/ontology.json#D_AVIATION
"""

from src.domains.d_aviation.implementation import (
    EnvelopeViolationError,
    CircuitBreaker,
    CircuitState,
    check_flight_envelope,
    parse_atc_message,
    compute_lift_mcn,
    ENVELOPE,
)


def check_envelope_overspeed_rejected() -> bool:
    """
    Invariant: Aircraft never enters a state violating safe-flight envelopes.
    Falsification: If overspeed is accepted without error, F_AVIATION_001 is violated.
    """
    raised = False
    try:
        check_flight_envelope(
            speed_kt=ENVELOPE["max_speed_kt"] + 1,
            altitude_ft=10_000,
            bank_deg=0,
            pitch_deg=0,
            vs_fpm=0,
        )
    except EnvelopeViolationError:
        raised = True
    assert raised, "Overspeed must raise EnvelopeViolationError — F_AVIATION_001 VIOLATED"
    return True


def check_envelope_normal_state_accepted() -> bool:
    """
    Invariant: Normal flight states within envelope must be accepted.
    Falsification: If a safe state raises an exception, the implementation over-restricts.
    """
    result = check_flight_envelope(
        speed_kt=250,
        altitude_ft=35_000,
        bank_deg=15,
        pitch_deg=5,
        vs_fpm=500,
    )
    assert result is True
    return True


def check_circuit_breaker_open_on_failures() -> bool:
    """
    Invariant: Circuit opens after failure_threshold consecutive failures.
    Falsification: If circuit stays CLOSED after threshold failures, F_AVIATION_004 is violated.
    """
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_s=60)
    assert cb.state == CircuitState.CLOSED

    def always_fails():
        raise ConnectionError("API down")

    for _ in range(3):
        cb.call("weather", always_fails, fallback={"wind_kt": 0})

    assert cb.state == CircuitState.OPEN, (
        f"Circuit should be OPEN after 3 failures, got {cb.state}"
    )
    return True


def check_circuit_breaker_returns_cache_when_open() -> bool:
    """
    Invariant: When circuit is OPEN, cached data is returned (no live API call).
    Falsification: If a live call is made when circuit is OPEN, F_AVIATION_004 is violated.
    """
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=60)
    cached = {"wind_kt": 15, "visibility_sm": 10}

    # One successful call to populate cache
    cb.call("weather", lambda: cached)
    cb.trip()
    assert cb.state == CircuitState.OPEN

    live_called = [False]

    def live_fetch():
        live_called[0] = True
        return {"wind_kt": 99}

    result = cb.call("weather", live_fetch, fallback=None)
    assert not live_called[0], "Live fetch was called while circuit is OPEN — F_AVIATION_004 VIOLATED"
    assert result == cached, f"Expected cached data, got {result}"
    return True


def check_malformed_atc_no_exception() -> bool:
    """
    Invariant: Malformed ATC messages never cause unhandled exceptions.
    Falsification: Any exception from parse_atc_message violates F_AVIATION_002.
    """
    malformed_inputs = ["", "X", "\x00\xff", "A" * 5000, "   ", None, 42]
    for inp in malformed_inputs:
        try:
            result = parse_atc_message(inp)
            assert isinstance(result, dict), f"Expected dict, got {type(result)} for {inp!r}"
            assert "error" in result or "callsign" in result
        except Exception as e:
            raise AssertionError(
                f"parse_atc_message raised unexpected exception for {inp!r}: {e}"
            )
    return True


def check_lift_deterministic() -> bool:
    """
    Invariant: Same inputs always produce identical lift (determinism).
    Falsification: Two calls with identical inputs return different values → F_AVIATION_001.
    """
    args = (250, 1225, 1000, 12, 10, 200)
    r1 = compute_lift_mcn(*args)
    r2 = compute_lift_mcn(*args)
    assert r1 == r2, f"Lift not deterministic: {r1} != {r2}"
    assert isinstance(r1, int), "Lift result must be integer"
    return True


def run_all_invariants() -> dict:
    """Run all D_AVIATION invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_envelope_overspeed_rejected,
        check_envelope_normal_state_accepted,
        check_circuit_breaker_open_on_failures,
        check_circuit_breaker_returns_cache_when_open,
        check_malformed_atc_no_exception,
        check_lift_deterministic,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_AVIATION invariants: PASS")
