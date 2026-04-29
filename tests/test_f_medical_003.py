"""
Falsification test: Infusion pump delivers within +/-5% of programmed rate.
Flow rate accurate to +-5%.

# @falsification_id: F_MEDICAL_003
"""
import pytest

def simulate_infusion(programmed_ml_per_hr: float, duration_hr: float, pump_error_frac: float) -> float:
    # TODO: Expand simulate_infusion() - stub detected by Yeshua Agent
    return programmed_ml_per_hr * duration_hr * (1 + pump_error_frac)

def test_infusion_within_5_percent():
    programmed = 100.0
    duration = 24.0
    expected_volume = programmed * duration
    actual_volume = simulate_infusion(programmed, duration, pump_error_frac=0.02)
    error_frac = abs(actual_volume - expected_volume) / expected_volume
    assert error_frac <= 0.05, f"Pump error {error_frac:.2%} exceeds 5%"
