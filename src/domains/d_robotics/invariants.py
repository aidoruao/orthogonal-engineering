#!/usr/bin/env python3
"""Robotics Domain Invariants — ISO 10218 safety compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    CollaborativeRobot, RobotMode, EmergencyStopSystem, SafetyZoneAnalyzer
)


def check_force_limits(robot: CollaborativeRobot) -> Tuple[bool, ProofObject]:
    """ISO/TS 15066: Collaborative robots must limit force to 150N.

    Falsifies if: robot is collaborative and max_force_exerted exceeds limit.
    """
    if robot.mode != RobotMode.COLLABORATIVE:
        return True, ProofObject(
            conclusion="Force limits not applicable in non-collaborative mode",
            premises=[],
            rule="iso_ts_15066_applicability"
        )
    
    max_force = robot.max_force_exerted()
    limit = robot.COLLABORATIVE_FORCE_LIMIT_N
    
    if max_force > limit:
        return False, ProofObject(
            conclusion=f"VIOLATION: Force {max_force}N exceeds collaborative limit {limit}N",
            premises=[f"Max force: {max_force}N", f"Limit: {limit}N"],
            rule="iso_ts_15066_force"
        )
    
    return True, ProofObject(
        conclusion=f"Force within collaborative limits ({max_force}N <= {limit}N)",
        premises=[],
        rule="iso_ts_15066_force"
    )


def check_emergency_stop_response(e_stop: EmergencyStopSystem) -> Tuple[bool, ProofObject]:
    """ISO 10218: Emergency stop must complete within 500ms.

    Falsifies if: triggered e-stop response exceeds MAX_RESPONSE_TIME_MS.
    """
    if not e_stop.e_stop_triggered:
        return True, ProofObject(
            conclusion="E-stop not triggered",
            premises=[],
            rule="e_stop_not_applicable"
        )
    
    response = e_stop.response_time()
    max_allowed = e_stop.MAX_RESPONSE_TIME_MS
    
    if response > max_allowed:
        return False, ProofObject(
            conclusion=f"VIOLATION: E-stop response {response}ms exceeds {max_allowed}ms",
            premises=[f"Response: {response}ms"],
            rule="iso_10218_estop"
        )
    
    return True, ProofObject(
        conclusion=f"E-stop response adequate ({response}ms <= {max_allowed}ms)",
        premises=[],
        rule="iso_10218_estop"
    )


def check_safety_zone_violations(analyzer: SafetyZoneAnalyzer) -> Tuple[bool, ProofObject]:
    """Safety zones must detect human presence.

    Falsifies if: human presence is detected in any safety zone.
    """
    if analyzer.human_in_any_zone():
        zone = analyzer.get_active_zone()
        return False, ProofObject(
            conclusion="VIOLATION: Human detected in safety zone",
            premises=[f"Zone: {zone.zone_id if zone else 'unknown'}"],
            rule="safety_zone_violation"
        )
    
    return True, ProofObject(
        conclusion="Safety zones clear",
        premises=[f"Zones checked: {len(analyzer.zones)}"],
        rule="safety_zone_clear"
    )


def check_collaborative_mode_constraints(robot: CollaborativeRobot) -> Tuple[bool, ProofObject]:
    """Collaborative mode requires force sensors and speed limits.

    Falsifies if: robot operates in collaborative mode without required force sensors.
    """
    if robot.mode != RobotMode.COLLABORATIVE:
        return True, ProofObject(
            conclusion="Not in collaborative mode",
            premises=[],
            rule="collaborative_mode_applicability"
        )
    
    if len(robot.force_sensors) == 0:
        return False, ProofObject(
            conclusion="VIOLATION: Collaborative mode requires force sensors",
            premises=[],
            rule="collaborative_requirements"
        )
    
    return True, ProofObject(
        conclusion="Collaborative mode requirements satisfied",
        premises=[f"Force sensors: {len(robot.force_sensors)}"],
        rule="collaborative_requirements"
    )
