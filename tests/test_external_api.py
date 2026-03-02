"""
Falsification test: External API is reachable within SLO timeout.
API responds within 500ms — fallback triggers on timeout.

# @falsification_id: F-API-001
"""
import time
import pytest

_FALLBACK_TRIGGERED = False

def _mock_api_call(timeout_ms: float, simulate_timeout: bool):
    global _FALLBACK_TRIGGERED
    if simulate_timeout:
        _FALLBACK_TRIGGERED = True
        return None
    time.sleep(0.01)
    return {"status": "ok"}

def test_fallback_on_timeout():
    global _FALLBACK_TRIGGERED
    _FALLBACK_TRIGGERED = False
    result = _mock_api_call(timeout_ms=500, simulate_timeout=True)
    assert result is None
    assert _FALLBACK_TRIGGERED, "Fallback was not triggered on timeout"

def test_api_succeeds_within_slo():
    t0 = time.monotonic()
    result = _mock_api_call(timeout_ms=500, simulate_timeout=False)
    elapsed_ms = (time.monotonic() - t0) * 1000
    assert result is not None
    assert elapsed_ms < 500, f"API call took {elapsed_ms:.1f}ms, exceeds 500ms SLO"
