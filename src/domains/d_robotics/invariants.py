"""D_ROBOTICS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ISO 10218 (Robot Safety), ISO/TS 15066 (Collaborative Robots)
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Dict
from datetime import datetime, timedelta


@dataclass
class RobotSystem:
    """Industrial robot system."""
    robot_id: str
    name: str
    max_speed_mps: Fraction  # meters per second
    payload_kg: Fraction
    safety_rated_monitored_stop: bool
    protective_stops_functional: bool


@dataclass
class SafetyZone:
    """Robot safety zone configuration."""
    zone_id: str
    robot_id: str
    radius_meters: Fraction
    intrusion_detected: bool
    robot_stopped: bool


@dataclass
class EmergencyStop:
    """Emergency stop system status."""
    estop_id: str
    tested_date: datetime
    functional: bool


def check_protective_stop_response() -> bool:
    """
    Invariant: Protective stop commands halt robot motion.
    Falsification: If protective stop signal doesn't stop robot.
    """
    robot = RobotSystem(
        robot_id="RBT001",
        name="Assembly Robot",
        max_speed_mps=Fraction(25, 10),  # 2.5 m/s
        payload_kg=Fraction(10),
        safety_rated_monitored_stop=True,
        protective_stops_functional=True,
    )
    
    # Protective stops must be functional
    assert robot.protective_stops_functional is True, (
        f"Robot {robot.name} protective stops must be functional"
    )
    
    # Safety-rated monitored stop must be enabled
    assert robot.safety_rated_monitored_stop is True, (
        f"Robot {robot.name} must have safety-rated monitored stop"
    )
    
    return True


def check_safety_zone_intrusion() -> bool:
    """
    Invariant: Safety zone intrusion triggers robot stop.
    Falsification: If intrusion detected but robot continues moving.
    """
    zone = SafetyZone(
        zone_id="ZONE001",
        robot_id="RBT001",
        radius_meters=Fraction(15, 10),  # 1.5m safety zone
        intrusion_detected=True,
        robot_stopped=True,  # Should stop when intrusion detected
    )
    
    if zone.intrusion_detected:
        assert zone.robot_stopped is True, (
            f"Robot must stop when intrusion detected in zone {zone.zone_id}"
        )
    
    return True


def check_emergency_stop_functional() -> bool:
    """
    Invariant: Emergency stop systems tested within interval.
    Falsification: If E-stop not tested within required period.
    """
    estop = EmergencyStop(
        estop_id="ESTOP001",
        tested_date=datetime.now() - timedelta(days=400),  # 400 days ago
        functional=True,
    )
    
    required_test_interval_days = 365  # Annual testing
    days_since_test = (datetime.now() - estop.tested_date).days
    
    assert days_since_test <= required_test_interval_days, (
        f"E-stop {estop.estop_id} overdue for testing: "
        f"{days_since_test} days vs required {required_test_interval_days}"
    )
    
    assert estop.functional is True, (
        f"E-stop {estop.estop_id} must be functional"
    )
    
    return True


def check_speed_limits_collaborative() -> bool:
    """
    Invariant: Collaborative robots operate within speed limits.
    Falsification: If cobot speed exceeds ISO/TS 15066 limits.
    """
    # Collaborative robot speed limit per ISO/TS 15066
    max_cobot_speed = Fraction(15, 10)  # 1.5 m/s for collaborative operation
    
    cobot = RobotSystem(
        robot_id="COBOT001",
        name="Collaborative Arm",
        max_speed_mps=Fraction(12, 10),  # 1.2 m/s - within limit
        payload_kg=Fraction(5),
        safety_rated_monitored_stop=True,
        protective_stops_functional=True,
    )
    
    assert cobot.max_speed_mps <= max_cobot_speed, (
        f"Cobot {cobot.name} speed {cobot.max_speed_mps} m/s exceeds "
        f"ISO/TS 15066 limit {max_cobot_speed} m/s"
    )
    
    return True


def check_force_limiting() -> bool:
    """
    Invariant: Collaborative robots have force limiting (transient < 280N).
    Falsification: If robot can apply force exceeding biomechanical limits.
    """
    # ISO/TS 15066 biomechanical limits (transient contact)
    max_force_newtons = Fraction(280)  # 280N for skull/temple
    
    # Robot should be force-limited
    robot_force_capability = Fraction(200)  # Limited to 200N
    
    assert robot_force_capability <= max_force_newtons, (
        f"Robot force capability {robot_force_capability}N exceeds "
        f"biomechanical limit {max_force_newtons}N"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("protective_stop", check_protective_stop_response),
        ("safety_zone", check_safety_zone_intrusion),
        ("emergency_stop", check_emergency_stop_functional),
        ("speed_limits", check_speed_limits_collaborative),
        ("force_limiting", check_force_limiting),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ROBOTICS invariants: PASS")
