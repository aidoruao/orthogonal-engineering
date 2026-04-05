"""
Falsification test suite for D_AVIATION domain.

Tests safe-flight envelope enforcement, circuit-breaker behavior, and ATC message parsing.

# @falsification_id: F_AVIATION_001, F_AVIATION_002, F_AVIATION_003, F_AVIATION_004
"""

import pytest
import time

from src.domains.d_aviation.implementation import (
    CircuitBreaker,
    CircuitState,
    EnvelopeViolationError,
    ENVELOPE,
    check_flight_envelope,
    compute_lift_mcn,
    parse_atc_message,
)


# ---------------------------------------------------------------------------
# F_AVIATION_001 — Safe-flight envelope enforcement
# ---------------------------------------------------------------------------

def test_normal_state_accepted():
    """A normal flight state must be accepted without error."""
    assert check_flight_envelope(250, 35_000, 15, 5, 500) is True


def test_overspeed_rejected():
    """Speed exceeding max envelope must raise EnvelopeViolationError."""
    with pytest.raises(EnvelopeViolationError):
        check_flight_envelope(
            speed_kt=ENVELOPE["max_speed_kt"] + 1,
            altitude_ft=10_000,
            bank_deg=0,
            pitch_deg=0,
            vs_fpm=0,
        )


def test_underspeed_rejected():
    """Speed below minimum (stall) must raise EnvelopeViolationError."""
    with pytest.raises(EnvelopeViolationError):
        check_flight_envelope(
            speed_kt=ENVELOPE["min_speed_kt"] - 1,
            altitude_ft=5_000,
            bank_deg=0,
            pitch_deg=0,
            vs_fpm=0,
        )


def test_altitude_above_ceiling_rejected():
    """Altitude above service ceiling must raise EnvelopeViolationError."""
    with pytest.raises(EnvelopeViolationError):
        check_flight_envelope(
            speed_kt=250,
            altitude_ft=ENVELOPE["max_altitude_ft"] + 1,
            bank_deg=0,
            pitch_deg=0,
            vs_fpm=0,
        )


def test_bank_angle_exceeded_rejected():
    """Bank angle beyond limit must raise EnvelopeViolationError."""
    with pytest.raises(EnvelopeViolationError):
        check_flight_envelope(
            speed_kt=250,
            altitude_ft=10_000,
            bank_deg=ENVELOPE["max_bank_deg"] + 1,
            pitch_deg=0,
            vs_fpm=0,
        )


def test_pitch_above_limit_rejected():
    """Pitch above max nose-up must raise EnvelopeViolationError."""
    with pytest.raises(EnvelopeViolationError):
        check_flight_envelope(
            speed_kt=250,
            altitude_ft=10_000,
            bank_deg=0,
            pitch_deg=ENVELOPE["max_pitch_up_deg"] + 1,
            vs_fpm=0,
        )


def test_envelope_rejects_float_input():
    """Envelope check must reject float inputs with ValueError."""
    with pytest.raises(ValueError):
        check_flight_envelope(250.5, 10_000, 0, 0, 0)  # type: ignore


# ---------------------------------------------------------------------------
# F_AVIATION_001 — Lift model determinism
# ---------------------------------------------------------------------------

def test_lift_model_deterministic():
    """Same inputs must produce identical lift result every time."""
    args = (250, 1225, 1000, 12, 10, 200)
    assert compute_lift_mcn(*args) == compute_lift_mcn(*args)


def test_lift_result_is_integer():
    """Lift result must be an integer (not float)."""
    result = compute_lift_mcn(200, 1225, 1000, 12, 10, 180)
    assert isinstance(result, int)


def test_lift_scales_with_speed_squared():
    """Doubling speed must quadruple lift (L ∝ v²)."""
    base = compute_lift_mcn(100, 1225, 1000, 10, 10, 100)
    doubled = compute_lift_mcn(200, 1225, 1000, 10, 10, 100)
    assert doubled == 4 * base


# ---------------------------------------------------------------------------
# F_AVIATION_002 — ATC message parsing
# ---------------------------------------------------------------------------

def test_valid_atc_message_parsed():
    """Valid ATC message produces structured dict with callsign and instruction."""
    result = parse_atc_message("UAL123 CLEARED TO FL350")
    assert result["callsign"] == "UAL123"
    assert result["instruction"] == "CLEARED"


def test_empty_message_returns_error():
    """Empty string returns error dict, not an exception."""
    result = parse_atc_message("")
    assert "error" in result


def test_too_short_message_returns_error():
    """Very short message returns error dict."""
    result = parse_atc_message("AB")
    assert "error" in result


def test_very_long_message_returns_error():
    """Extremely long message returns error dict (DoS protection)."""
    result = parse_atc_message("X" * 3000)
    assert "error" in result


def test_null_bytes_no_exception():
    """Null bytes and binary garbage must not raise any exception."""
    result = parse_atc_message("\x00\xff\x00")
    assert isinstance(result, dict)


def test_non_string_returns_error():
    """Non-string input must return error dict, not raise."""
    result = parse_atc_message(None)  # type: ignore
    assert "error" in result


# ---------------------------------------------------------------------------
# F_AVIATION_004 — Circuit breaker
# ---------------------------------------------------------------------------

def test_circuit_opens_after_threshold():
    """Circuit must open after failure_threshold consecutive failures."""
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_s=60)

    def fails():
        raise ConnectionError("down")

    for _ in range(3):
        cb.call("wx", fails, fallback={})

    assert cb.state == CircuitState.OPEN


def test_circuit_returns_cache_when_open():
    """Open circuit must return cached data without calling live fetch."""
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=60)
    stale = {"wind_kt": 10}
    cb.call("wx", lambda: stale)
    cb.trip()

    live_calls = [0]

    def live():
        live_calls[0] += 1
        return {"wind_kt": 99}

    result = cb.call("wx", live)
    assert live_calls[0] == 0, "Live fetch must not be called when circuit is OPEN"
    assert result == stale


def test_circuit_fallback_when_no_cache():
    """Open circuit with no cache must return fallback value."""
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=60)
    cb.trip()
    fallback = {"wind_kt": 0}
    result = cb.call("wx", lambda: {"wind_kt": 99}, fallback=fallback)
    assert result == fallback


def test_circuit_resets_after_successful_probe():
    """After healing, a successful probe must close the circuit."""
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=1)
    cb.trip()
    # Force transition to HALF_OPEN by backdating the opened_at timestamp
    cb._opened_at = time.monotonic() - 2  # 2 seconds ago, beyond recovery_timeout_s=1
    assert cb.state == CircuitState.HALF_OPEN

    result = cb.call("wx", lambda: {"wind_kt": 5})
    assert cb.state == CircuitState.CLOSED
    assert result == {"wind_kt": 5}
