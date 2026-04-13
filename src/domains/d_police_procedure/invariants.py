"""D_POLICE_PROCEDURE invariants — Yeshua Standard. 0 floats.

Standards:
- Terry v. Ohio, 392 U.S. 1 (1968) — stop-and-frisk
- Mapp v. Ohio, 367 U.S. 643 (1961) — exclusionary rule
- Miranda v. Arizona, 384 U.S. 436 (1966) — custodial interrogation
- DOJ Consent Decree framework
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import BodyCamera, CitizenEncounter


def check_body_camera_activation(camera: BodyCamera, encounter: CitizenEncounter) -> Tuple[bool, ProofObject]:
    """Body camera must be activated at start of any citizen encounter.

    Standard: DOJ Body-Worn Camera Policy and Implementation Program
    falsifies_if: encounter.camera_activated is False when encounter occurred.
    """
    ok = encounter.camera_activated
    premises = [
        f"encounter_id={encounter.encounter_id}",
        f"officer_id={encounter.officer_id}",
        f"camera_id={camera.camera_id}",
        f"camera_activated={encounter.camera_activated}",
    ]
    return ok, ProofObject(
        rule="BodyCameraActivation",
        premises=premises,
        conclusion="PASS: body camera activated" if ok else "VIOLATION: body camera not activated during encounter",
    )


def check_camera_battery_sufficient(camera: BodyCamera) -> Tuple[bool, ProofObject]:
    """Camera battery must be ≥20% before deployment.

    Standard: DOJ BWC implementation — minimum operational readiness
    falsifies_if: camera.battery_level < Fraction(20).
    """
    min_battery = Fraction(20)
    ok = camera.battery_level >= min_battery
    premises = [
        f"camera_id={camera.camera_id}",
        f"battery_level={camera.battery_level}",
        f"min_required={min_battery}",
    ]
    return ok, ProofObject(
        rule="CameraBatterySufficient",
        premises=premises,
        conclusion=f"PASS: battery {camera.battery_level}% >= {min_battery}%" if ok else f"VIOLATION: battery {camera.battery_level}% < {min_battery}%",
    )


def check_storage_available(camera: BodyCamera) -> Tuple[bool, ProofObject]:
    """Camera must have storage available to record.

    Standard: DOJ BWC implementation requirements
    falsifies_if: camera.storage_available is False.
    """
    ok = camera.storage_available
    premises = [
        f"camera_id={camera.camera_id}",
        f"storage_available={camera.storage_available}",
    ]
    return ok, ProofObject(
        rule="StorageAvailable",
        premises=premises,
        conclusion="PASS: storage available" if ok else "VIOLATION: no storage — camera cannot record",
    )


def check_encounter_documented(encounter: CitizenEncounter) -> Tuple[bool, ProofObject]:
    """Every citizen encounter must have officer and encounter IDs.

    Standard: DOJ accountability framework; 42 U.S.C. §3789d
    falsifies_if: encounter_id or officer_id is empty.
    """
    ok = bool(encounter.encounter_id.strip()) and bool(encounter.officer_id.strip())
    premises = [
        f"encounter_id={encounter.encounter_id!r}",
        f"officer_id={encounter.officer_id!r}",
    ]
    return ok, ProofObject(
        rule="EncounterDocumented",
        premises=premises,
        conclusion="PASS: encounter documented" if ok else "VIOLATION: encounter missing ID",
    )


def check_recordings_logged(camera: BodyCamera) -> Tuple[bool, ProofObject]:
    """Camera with recording enabled must have ≥1 recording logged at end of shift.

    Standard: DOJ BWC evidence integrity
    falsifies_if: camera.recording is True but camera.recordings_count == 0.
    """
    if camera.recording:
        ok = camera.recordings_count >= 1
    else:
        ok = True
    premises = [
        f"camera_id={camera.camera_id}",
        f"recording={camera.recording}",
        f"recordings_count={camera.recordings_count}",
    ]
    return ok, ProofObject(
        rule="RecordingsLogged",
        premises=premises,
        conclusion="PASS: recordings properly logged" if ok else "VIOLATION: recording active but no recordings logged",
    )


def check_encounter_location_set(encounter: CitizenEncounter) -> Tuple[bool, ProofObject]:
    """Encounter location must be non-empty for accountability.

    Standard: DOJ consent decree location-reporting requirements
    falsifies_if: encounter.location is empty.
    """
    ok = bool(encounter.location.strip())
    premises = [
        f"encounter_id={encounter.encounter_id}",
        f"location_set={ok}",
    ]
    return ok, ProofObject(
        rule="EncounterLocationSet",
        premises=premises,
        conclusion="PASS: encounter location documented" if ok else "VIOLATION: encounter location missing",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    from datetime import datetime
    camera = BodyCamera(
        camera_id="CAM-001", officer_id="OFF-001", serial_number="SN-12345",
        activated=True, recording=True, battery_level=Fraction(95),
        storage_available=True, recordings_count=3,
    )
    from datetime import datetime as dt
    from .implementation import EncounterType
    encounter = CitizenEncounter(
        encounter_id="ENC-001", officer_id="OFF-001",
        officer_camera_id="CAM-001",
        encounter_type=list(EncounterType)[0],
        start_time=dt(2024, 1, 1, 10, 0),
        location="123 Main St", camera_activated=True,
    )
    results = {}
    for fn, args in [
        (check_body_camera_activation, (camera, encounter)),
        (check_camera_battery_sufficient, (camera,)),
        (check_storage_available, (camera,)),
        (check_encounter_documented, (encounter,)),
        (check_recordings_logged, (camera,)),
        (check_encounter_location_set, (encounter,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
