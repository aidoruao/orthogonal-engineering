#!/usr/bin/env python3
"""Rail Domain Invariants — FRA compliance, PTC, safety.

Standards:
- 49 CFR (FRA regulations)
- PTC mandate
- Hours of service
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import RailVehicle, Train, TrackSegment


def check_inspection_current(vehicle: RailVehicle) -> Tuple[bool, ProofObject]:
    if not vehicle.inspection_current():
        days_overdue = (datetime.now() - vehicle.inspection_due).days
        return False, ProofObject(
            conclusion=f"VIOLATION: Inspection overdue {days_overdue} days",
            premises=[f"Vehicle: {vehicle.vehicle_id}"],
            rule="49_cfr_215_inspection"
        )
    return True, ProofObject(
        conclusion="Inspection current",
        premises=[],
        rule="inspection_compliant"
    )


def check_speed_limit(train: Train) -> Tuple[bool, ProofObject]:
    if not train.speed_compliant():
        return False, ProofObject(
            conclusion=f"VIOLATION: Speed {train.max_speed} exceeds authorized {train.authorized_speed}",
            premises=[f"Train: {train.train_id}"],
            rule="49_cfr_236_speed"
        )
    return True, ProofObject(
        conclusion="Speed compliant",
        premises=[],
        rule="speed_compliant"
    )


def check_hours_of_service(train: Train) -> Tuple[bool, ProofObject]:
    MAX_HOURS = Fraction(12)
    if train.hours_of_service > MAX_HOURS:
        return False, ProofObject(
            conclusion=f"VIOLATION: Hours {train.hours_of_service} exceed limit {MAX_HOURS}",
            premises=[f"Train: {train.train_id}"],
            rule="49_cfr_228_hours_of_service"
        )
    return True, ProofObject(
        conclusion="Hours within limit",
        premises=[],
        rule="hours_compliant"
    )


def check_ptc_equipped(vehicle: RailVehicle) -> Tuple[bool, ProofObject]:
    if not vehicle.ptc_equipped:
        return False, ProofObject(
            conclusion="VIOLATION: Vehicle not PTC equipped",
            premises=[f"Vehicle: {vehicle.vehicle_id}"],
            rule="rsia_ptc_mandate"
        )
    return True, ProofObject(
        conclusion="PTC equipped",
        premises=[],
        rule="ptc_compliant"
    )


def check_track_class_speed(track: TrackSegment) -> Tuple[bool, ProofObject]:
    """Track class determines maximum speed."""
    class_speeds = {1: 10, 2: 25, 3: 40, 4: 60, 5: 80, 6: 110}
    max_allowed = class_speeds.get(track.track_class, 10)
    if track.max_speed > max_allowed:
        return False, ProofObject(
            conclusion=f"VIOLATION: Track speed {track.max_speed} exceeds class {track.track_class} limit {max_allowed}",
            premises=[],
            rule="49_cfr_213_track_speed"
        )
    return True, ProofObject(
        conclusion="Track speed appropriate",
        premises=[],
        rule="track_speed_compliant"
    )
