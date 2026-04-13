"""D_INDUSTRIAL Invariants — OSHA Safety, Machine Guarding, Industrial Hygiene

Verifies OSHA recordkeeping, incident rates, machine safety,
willful violations, industry safety standards.

Standards: 29 U.S.C. § 651 (OSH Act), 29 CFR 1910, ANSI Z10
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import IndustrialFacility, MachineSafety, ViolationSeverity, osha_trir_target, osha_dart_target


def check_osha_trir(facility: IndustrialFacility) -> Tuple[bool, ProofObject]:
    """
    OSHA Total Recordable Incident Rate should be controlled.
    
    Industry benchmarks:
    - TRIR < 3.0 good performance
    - TRIR > 6.0 requires intervention
    - Trend analysis important
    
    Falsifies if: TRIR > 6.0
    falsifies_if: TRIR > 6.0
    """
    max_trir = Fraction(6)  # 6.0 per 200,000 hours
    trir = facility.get_trifr()
    
    if trir > max_trir:
        return False, ProofObject(
            conclusion=f"VIOLATION: Facility {facility.name} TRIR {trir} exceeds maximum {max_trir}",
            premises=[
                f"Recordable incidents: {facility.osha_recordable_incidents}",
                f"Hours worked: {facility.total_hours_worked}",
                f"TRIR: {trir}",
                "OSHA recordkeeping — Incident rate"
            ],
            rule="osha_trir"
        )
    
    return True, ProofObject(
        conclusion=f"Facility {facility.name} TRIR acceptable",
        premises=[f"TRIR: {trir}"],
        rule="osha_trir"
    )


def check_osha_dart(facility: IndustrialFacility) -> Tuple[bool, ProofObject]:
    """
    DART rate indicates severity of injuries.
    
    Days Away, Restricted, or Transferred:
    - DART < 2.0 good performance
    - DART > 3.0 intervention required
    - Leading indicator of serious injuries
    
    Falsifies if: DART > 3.0
    falsifies_if: DART > 3.0
    """
    max_dart = Fraction(3)  # 3.0 per 200,000 hours
    dart = facility.get_dart_rate()
    
    if dart > max_dart:
        return False, ProofObject(
            conclusion=f"VIOLATION: Facility {facility.name} DART {dart} exceeds {max_dart}",
            premises=[
                f"DART cases: {facility.days_away_restricted}",
                f"Hours: {facility.total_hours_worked}",
                f"DART: {dart}",
                "OSHA — Severity indicator"
            ],
            rule="osha_dart"
        )
    
    return True, ProofObject(
        conclusion=f"Facility {facility.name} DART rate acceptable",
        premises=[f"DART: {dart}"],
        rule="osha_dart"
    )


def check_willful_violations(facility: IndustrialFacility) -> Tuple[bool, ProofObject]:
    """
    Willful violations indicate intentional non-compliance.
    
    OSHA enforcement:
    - Willful violations carry criminal penalties
    - Shows disregard for employee safety
    - High penalties ($145,027 per violation)
    
    Falsifies if: any willful violations
    falsifies_if: any willful violations
    """
    if facility.willful_violations > 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: Facility {facility.name} has {facility.willful_violations} willful OSHA violations",
            premises=[
                f"Willful: {facility.willful_violations}",
                f"Serious: {facility.serious_violations}",
                "29 U.S.C. § 666 — Willful violations"
            ],
            rule="willful_violations"
        )
    
    return True, ProofObject(
        conclusion=f"Facility {facility.name} no willful violations",
        premises=["Willful: 0"],
        rule="willful_violations"
    )


def check_machine_guarding(safety: MachineSafety) -> Tuple[bool, ProofObject]:
    """
    Machine guards required at point of operation.
    
    29 CFR § 1910.212:
    - Point of operation guarding
    - Interlocks functional
    - Emergency stop available
    
    Falsifies if: missing guards on hazardous machines
    falsifies_if: missing guards on hazardous machines
    """
    if not safety.point_of_operation_guard:
        return False, ProofObject(
            conclusion=f"VIOLATION: Machine {safety.machine_id} missing point of operation guard",
            premises=[
                f"Point guard: {safety.point_of_operation_guard}",
                "29 CFR § 1910.212 — Machine guarding"
            ],
            rule="machine_guarding"
        )
    
    if not safety.emergency_stop:
        return False, ProofObject(
            conclusion=f"VIOLATION: Machine {safety.machine_id} missing emergency stop",
            premises=[
                f"E-stop: {safety.emergency_stop}",
                "Machine safety — Emergency stop required"
            ],
            rule="machine_guarding"
        )
    
    return True, ProofObject(
        conclusion=f"Machine {safety.machine_id} guarding compliant",
        premises=[
            f"Point guard: {safety.point_of_operation_guard}",
            f"E-stop: {safety.emergency_stop}"
        ],
        rule="machine_guarding"
    )


def check_lockout_tagout(safety: MachineSafety) -> Tuple[bool, ProofObject]:
    """
    Lockout/tagout required for maintenance.
    
    29 CFR § 1910.147:
    - Energy control procedures
    - Locks and tags
    - Periodic inspection
    
    Falsifies if: LOTO procedures not in place
    falsifies_if: LOTO procedures not in place
    """
    if not safety.lockout_tagout_procedures:
        return False, ProofObject(
            conclusion=f"VIOLATION: Machine {safety.machine_id} lacks lockout/tagout procedures",
            premises=[
                f"LOTO: {safety.lockout_tagout_procedures}",
                "29 CFR § 1910.147 — Control of hazardous energy"
            ],
            rule="lockout_tagout"
        )
    
    return True, ProofObject(
        conclusion=f"Machine {safety.machine_id} LOTO procedures verified",
        premises=["LOTO: YES"],
        rule="lockout_tagout"
    )
