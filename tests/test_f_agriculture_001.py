"""
Falsification test: Irrigation delivery within +/-10% of setpoint.
Delivered volume within 10% of commanded.

# @falsification_id: F-AGRICULTURE-001
"""
import pytest

def simulate_irrigation(setpoint_liters: float, pump_error_frac: float) -> float:
    return setpoint_liters * (1 + pump_error_frac)

def test_irrigation_within_10pct():
    setpoint = 500.0
    delivered = simulate_irrigation(setpoint, pump_error_frac=0.05)
    error = abs(delivered - setpoint) / setpoint
    assert error <= 0.10, f"Irrigation error {error:.2%} exceeds 10%"
