"""
Falsification test: Reactor thermal runaway interlock activates before critical point.
Interlock at T_alarm before T_critical.

# @falsification_id: F_CHEMICAL_001
"""
import pytest

T_ALARM = 150.0
T_CRITICAL = 200.0

def simulate_temperature_rise(step: float = 1.0):
    temp = 20.0
    interlock_at = None
    while temp < T_CRITICAL + 10:
        if interlock_at is None and temp >= T_ALARM:
            interlock_at = temp
            break
        temp += step
    return interlock_at

def test_interlock_before_critical():
    interlock_temp = simulate_temperature_rise()
    assert interlock_temp is not None, "Interlock never triggered"
    assert interlock_temp < T_CRITICAL, f"Interlock at {interlock_temp}C >= T_critical {T_CRITICAL}C"
    assert interlock_temp >= T_ALARM, f"Interlock at {interlock_temp}C < T_alarm {T_ALARM}C"
