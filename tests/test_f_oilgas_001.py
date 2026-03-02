"""
Falsification test: Pipeline pressure anomaly detected within 60 seconds.
Leak detected within 60s.

# @falsification_id: F_OILGAS_001
"""
import pytest

def simulate_leak_detection(pressure_drop_rate: float, detection_threshold: float, poll_interval_s: float) -> float:
    """Returns time in seconds to detect leak."""
    pressure = 100.0
    t = 0.0
    while t <= 120.0:
        pressure -= pressure_drop_rate * poll_interval_s
        if pressure < detection_threshold:
            return t
        t += poll_interval_s
    return float("inf")

def test_leak_detected_within_60s():
    detection_time = simulate_leak_detection(
        pressure_drop_rate=2.0,
        detection_threshold=80.0,
        poll_interval_s=1.0
    )
    assert detection_time <= 60.0, f"Leak detected at {detection_time}s, exceeds 60s"
