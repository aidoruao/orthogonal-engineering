"""
Falsification test: Water quality sensor alerts before threshold breach.
Sensor fires alert before reading exceeds limit.

# @falsification_id: F-WATER-001
"""
import pytest

ALERT_THRESHOLD = 0.9
LIMIT = 1.0

def simulate_sensor_readings():
    return [i * 0.1 for i in range(12)]

def check_alert(readings: list, alert_threshold: float, limit: float) -> dict:
    alert_fired_at = None
    breach_at = None
    for val in readings:
        if alert_fired_at is None and val >= alert_threshold:
            alert_fired_at = val
        if breach_at is None and val >= limit:
            breach_at = val
    return {"alert": alert_fired_at, "breach": breach_at}

def test_alert_fires_before_breach():
    readings = simulate_sensor_readings()
    result = check_alert(readings, ALERT_THRESHOLD, LIMIT)
    assert result["alert"] is not None, "Alert never fired"
    assert result["breach"] is not None, "Breach never occurred"
    assert result["alert"] < result["breach"], "Alert must fire before breach"
