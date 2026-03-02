"""
Falsification test: Heavy equipment proximity halt.
Worker in zone triggers halt within stopping distance.

# @falsification_id: F-BLUECOLLAR-004
"""
import pytest

STOPPING_DISTANCE_M = 2.0

def simulate_proximity_halt(worker_distance_m: float, equipment_speed_mps: float, reaction_time_s: float) -> dict:
    distance_traveled = equipment_speed_mps * reaction_time_s
    halted_before_contact = distance_traveled < worker_distance_m
    return {"distance_traveled": distance_traveled, "halted": halted_before_contact}

def test_halt_before_stopping_distance():
    result = simulate_proximity_halt(
        worker_distance_m=STOPPING_DISTANCE_M,
        equipment_speed_mps=0.5,
        reaction_time_s=0.1
    )
    assert result["halted"], f"Equipment did not halt in time: traveled {result['distance_traveled']:.2f}m"
