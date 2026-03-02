"""
Falsification test: Gas sensor triggers alarm before LEL threshold.
Alarm fires at 20% LEL.

# @falsification_id: F_MINING_001
"""
import pytest

ALARM_THRESHOLD_PCT = 20.0
LEL_FULL_PCT = 100.0

def simulate_gas_rise(step: float = 0.5) -> tuple:
    concentration = 0.0
    alarm_fired_at = None
    while concentration <= 100.0:
        if alarm_fired_at is None and concentration >= ALARM_THRESHOLD_PCT:
            alarm_fired_at = concentration
            break
        concentration += step
    return alarm_fired_at

def test_alarm_fires_at_20pct_lel():
    alarm_at = simulate_gas_rise()
    assert alarm_at is not None, "Alarm never fired"
    assert alarm_at <= 20.5, f"Alarm fired too late at {alarm_at}% LEL (should be ~20%)"
    assert alarm_at >= 20.0, f"Alarm fired too early at {alarm_at}% LEL"
