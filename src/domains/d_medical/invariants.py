"""D_MEDICAL invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: FDA 21 CFR Part 820 (QSR), HIPAA, EMTALA
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Dict, Optional
from datetime import datetime, timedelta


@dataclass
class MedicalDevice:
    """Medical device with risk classification."""
    device_id: str
    name: str
    risk_class: str  # Class I, II, III
    has_510k_clearance: bool
    has_pma: bool  # Pre-Market Approval
    qsr_compliant: bool


@dataclass
class PatientRecord:
    """Patient health information."""
    record_id: str
    patient_id: str
    phi_disclosed: bool
    minimum_necessary_used: bool
    patient_authorization: bool


@dataclass
class EMTALAScreening:
    """EMTALA medical screening exam."""
    screening_id: str
    patient_id: str
    screening_completed: bool
    emergency_medical_condition: bool
    stabilization_provided: bool
    transferred: bool
    transfer_appropriate: bool


def check_device_classification_matches_risk() -> bool:
    """
    Invariant: Device classification matches risk level (Class III = life-supporting).
    Falsification: If high-risk device has lower classification.
    """
    # Class III device (life-supporting/life-sustaining)
    pacemaker = MedicalDevice(
        device_id="DEV001",
        name="Cardiac Pacemaker",
        risk_class="III",
        has_510k_clearance=False,  # Class III requires PMA, not 510(k)
        has_pma=True,
        qsr_compliant=True,
    )
    
    # Class III must have PMA
    if pacemaker.risk_class == "III":
        assert pacemaker.has_pma is True, (
            f"Class III device {pacemaker.name} must have PMA"
        )
        assert pacemaker.has_510k_clearance is False, (
            f"Class III device {pacemaker.name} cannot use 510(k)"
        )
    
    # Class I device (low risk)
    tongue_depressor = MedicalDevice(
        device_id="DEV002",
        name="Tongue Depressor",
        risk_class="I",
        has_510k_clearance=False,  # Most Class I exempt
        has_pma=False,
        qsr_compliant=True,
    )
    
    assert tongue_depressor.risk_class == "I", "Should be Class I"
    
    return True


def check_qsr_compliance() -> bool:
    """
    Invariant: Medical device manufacturers comply with Quality System Regulation.
    Falsification: If non-QSR-compliant device manufacturing passes audit.
    """
    device = MedicalDevice(
        device_id="DEV003",
        name="Surgical Instrument",
        risk_class="II",
        has_510k_clearance=True,
        has_pma=False,
        qsr_compliant=False,  # Not compliant!
    )
    
    assert device.qsr_compliant is True, (
        f"Device {device.name} must comply with 21 CFR Part 820 QSR"
    )
    
    return True


def check_hipaa_minimum_necessary() -> bool:
    """
    Invariant: PHI disclosure limited to minimum necessary.
    Falsification: If disclosure exceeds minimum necessary for purpose.
    """
    record = PatientRecord(
        record_id="REC001",
        patient_id="PAT001",
        phi_disclosed=True,
        minimum_necessary_used=False,  # Too much disclosed!
        patient_authorization=True,
    )
    
    if record.phi_disclosed:
        assert record.minimum_necessary_used is True, (
            f"PHI disclosure for {record.patient_id} must use minimum necessary standard"
        )
    
    return True


def check_patient_authorization_for_phi() -> bool:
    """
    Invariant: PHI disclosure requires patient authorization (with exceptions).
    Falsification: If unauthorized disclosure not for permitted purpose.
    """
    record = PatientRecord(
        record_id="REC002",
        patient_id="PAT002",
        phi_disclosed=True,
        minimum_necessary_used=True,
        patient_authorization=False,  # No authorization!
    )
    
    # If no authorization, must be for permitted purpose (treatment, payment, ops)
    # Here we're checking a non-permitted disclosure
    assert record.patient_authorization is True, (
        f"PHI disclosure for {record.patient_id} requires authorization "
        f"unless for permitted purpose (TPO)"
    )
    
    return True


def check_emtala_screening_required() -> bool:
    """
    Invariant: Hospital provides medical screening exam regardless of ability to pay.
    Falsification: If patient turned away without MSE.
    """
    screening = EMTALAScreening(
        screening_id="SCR001",
        patient_id="PAT003",
        screening_completed=False,  # Not screened!
        emergency_medical_condition=True,
        stabilization_provided=False,
        transferred=False,
        transfer_appropriate=False,
    )
    
    assert screening.screening_completed is True, (
        f"EMTALA requires medical screening exam for {screening.patient_id}"
    )
    
    return True


def check_emtala_stabilization() -> bool:
    """
    Invariant: Emergency medical condition requires stabilization before transfer.
    Falsification: If unstable patient transferred inappropriately.
    """
    screening = EMTALAScreening(
        screening_id="SCR002",
        patient_id="PAT004",
        screening_completed=True,
        emergency_medical_condition=True,
        stabilization_provided=False,  # Not stabilized!
        transferred=True,  # But transferred!
        transfer_appropriate=False,
    )
    
    if screening.emergency_medical_condition and screening.transferred:
        assert screening.stabilization_provided is True, (
            f"Patient {screening.patient_id} with EMC must be stabilized "
            f"before transfer (or appropriate transfer certification)"
        )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("device_classification", check_device_classification_matches_risk),
        ("qsr_compliance", check_qsr_compliance),
        ("hipaa_minimum", check_hipaa_minimum_necessary),
        ("phi_authorization", check_patient_authorization_for_phi),
        ("emtala_screening", check_emtala_screening_required),
        ("emtala_stabilization", check_emtala_stabilization),
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
    print("All D_MEDICAL invariants: PASS")
