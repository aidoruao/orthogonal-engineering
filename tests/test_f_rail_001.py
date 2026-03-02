"""
Falsification test: Positive train control stops train before red signal.
PTC halts train before stop signal.

# @falsification_id: F_RAIL_001
"""
import pytest

SIGNAL_POSITION_M = 500.0
BRAKE_DISTANCE_M = 200.0

def simulate_ptc(train_position_m: float, speed_mps: float, brake_decel: float) -> dict:
    distance_to_signal = SIGNAL_POSITION_M - train_position_m
    brake_issued = distance_to_signal <= BRAKE_DISTANCE_M
    stopping_distance = (speed_mps ** 2) / (2 * brake_decel)
    stops_in_time = stopping_distance <= distance_to_signal
    return {"brake_issued": brake_issued, "stops_in_time": stops_in_time}

def test_ptc_halts_before_signal():
    # Train at 320m from origin, 180m from signal; speed 20 m/s, decel 2.0 m/s^2
    # stopping_distance = 20^2 / (2*2.0) = 100m <= 180m distance_to_signal
    result = simulate_ptc(
        train_position_m=320.0,
        speed_mps=20.0,
        brake_decel=2.0
    )
    assert result["brake_issued"], "PTC brake command not issued"
    assert result["stops_in_time"], "Train cannot stop before signal"
