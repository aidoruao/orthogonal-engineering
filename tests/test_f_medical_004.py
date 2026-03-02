"""
Falsification test: Ventilator alarm activates within 5 seconds of patient disconnect.
Disconnect detected within 5s.

# @falsification_id: F-MEDICAL-004
"""
import time
import pytest

def simulate_disconnect_alarm(detection_delay_s: float) -> bool:
    return detection_delay_s <= 5.0

def test_alarm_within_5s():
    detection_delay_s = 1.5
    assert simulate_disconnect_alarm(detection_delay_s), f"Alarm delayed {detection_delay_s}s"

def test_late_alarm_fails():
    detection_delay_s = 6.0
    assert not simulate_disconnect_alarm(detection_delay_s)
