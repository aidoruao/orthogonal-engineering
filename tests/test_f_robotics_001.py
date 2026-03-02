"""
Falsification test: Robot arm stops within collision-avoidance envelope.
Arm halts before contacting obstacle.

# @falsification_id: F-ROBOTICS-001
"""
import pytest

OBSTACLE_POSITION_M = 1.0
SAFETY_MARGIN_M = 0.1
STOP_DISTANCE_M = OBSTACLE_POSITION_M - SAFETY_MARGIN_M

def simulate_arm_movement(start_m: float, step_m: float, obstacle_m: float, safety_m: float):
    pos = start_m
    stop_issued = False
    while pos < obstacle_m:
        if pos >= obstacle_m - safety_m:
            stop_issued = True
            break
        pos += step_m
    return {"stopped_at": pos, "stop_issued": stop_issued, "contact": pos >= obstacle_m}

def test_arm_stops_before_obstacle():
    result = simulate_arm_movement(0.0, 0.05, OBSTACLE_POSITION_M, SAFETY_MARGIN_M)
    assert result["stop_issued"], "Stop command was not issued"
    assert not result["contact"], f"Arm contacted obstacle at {result['stopped_at']:.2f}m"
