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
    """FRA requires current rolling stock inspection.

    Falsifies if: inspection_current returns False.
    falsifies_if: inspection_current returns False.
    """
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
    """Train speed must not exceed authorized limits.

    Falsifies if: speed_compliant returns False.
    falsifies_if: speed_compliant returns False.
    """
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
    """Crew hours of service limited under 49 CFR 228.

    Falsifies if: hours_of_service exceeds 12 hours.
    falsifies_if: hours_of_service exceeds 12 hours.
    """
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
    """Positive Train Control (PTC) required where mandated.

    Falsifies if: ptc_equipped is False.
    falsifies_if: ptc_equipped is False.
    """
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
    """Track class determines maximum speed.

    Falsifies if: track.max_speed exceeds allowed speed for track_class.
    falsifies_if: track.max_speed exceeds allowed speed for track_class.
    """
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


def run_all_invariants() -> dict:
    """Run all D_RAIL invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    train = Train(
        train_id=None,
        locomotive=None,
        cars=None,
        crew_size=None,
        hours_of_service=Fraction(1),
        max_speed=None,
        authorized_speed=None,
    )
    rail_vehicle = RailVehicle(
        vehicle_id=None,
        vehicle_type=None,
        inspection_date=None,
        inspection_due=None,
        max_speed_mph=None,
        ptc_equipped=None,
        ptc_operational=None,
    )
    track_segment = TrackSegment(
        segment_id=None,
        milepost_start=None,
        milepost_end=None,
        track_class=None,
        max_speed=None,
        inspection_date=None,
        defects_found=None,
    )

    checks = [
        ("check_hours_of_service", lambda: check_hours_of_service(train)),
        ("check_inspection_current", lambda: check_inspection_current(rail_vehicle)),
        ("check_ptc_equipped", lambda: check_ptc_equipped(rail_vehicle)),
        ("check_speed_limit", lambda: check_speed_limit(train)),
        ("check_track_class_speed", lambda: check_track_class_speed(track_segment)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_RAIL invariants: PASS")
