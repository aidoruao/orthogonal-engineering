"""D_LABOR_RIGHTS invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes FLSA, OSHA,
FMLA, and NLRA labor rights requirements.

Standards:
- FLSA (29 U.S.C. §206-207)
- OSHA (29 U.S.C. §654)
- FMLA (29 U.S.C. §2612)
- NLRA (29 U.S.C. §157)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import WorkplaceRecord


def check_minimum_wage(record: WorkplaceRecord) -> Tuple[bool, ProofObject]:
    """
    Rule: Hourly wage must meet or exceed the federal minimum wage (FLSA 29 U.S.C. §206).

    falsifies_if: hourly_wage < federal_minimum_wage.
    """
    success = record.hourly_wage >= record.federal_minimum_wage

    if not success:
        return False, ProofObject(
            rule="FLSAMinimumWage",
            premises=[
                f"record_id={record.record_id}",
                f"hourly_wage={record.hourly_wage}",
                f"federal_minimum_wage={record.federal_minimum_wage}",
            ],
            conclusion="VIOLATION: FLSA §206 — hourly wage below federal minimum wage",
        )

    return True, ProofObject(
        rule="FLSAMinimumWage",
        premises=[
            f"record_id={record.record_id}",
            f"hourly_wage={record.hourly_wage}",
            f"federal_minimum_wage={record.federal_minimum_wage}",
        ],
        conclusion="FLSA §206 minimum wage requirement satisfied",
    )


def check_overtime_rate(record: WorkplaceRecord) -> Tuple[bool, ProofObject]:
    """
    Rule: Overtime must be compensated at 1.5x the regular rate (FLSA 29 U.S.C. §207).

    falsifies_if: overtime_hours > 0 AND overtime_rate_multiplier < Fraction(3, 2).
    """
    if record.overtime_hours > Fraction(0):
        success = record.overtime_rate_multiplier >= Fraction(3, 2)
    else:
        success = True

    if not success:
        return False, ProofObject(
            rule="FLSAOvertimeRate",
            premises=[
                f"record_id={record.record_id}",
                f"overtime_hours={record.overtime_hours}",
                f"overtime_rate_multiplier={record.overtime_rate_multiplier}",
                f"required_multiplier={Fraction(3, 2)}",
            ],
            conclusion="VIOLATION: FLSA §207 — overtime rate below 1.5x regular rate",
        )

    return True, ProofObject(
        rule="FLSAOvertimeRate",
        premises=[
            f"record_id={record.record_id}",
            f"overtime_hours={record.overtime_hours}",
            f"overtime_rate_multiplier={record.overtime_rate_multiplier}",
        ],
        conclusion="FLSA §207 overtime rate requirement satisfied",
    )


def check_osha_recordkeeping(record: WorkplaceRecord) -> Tuple[bool, ProofObject]:
    """
    Rule: OSHA-recordable incidents must be reported (OSHA 29 U.S.C. §654, 29 CFR 1904).

    falsifies_if: osha_recordable_incident is True AND incident_reported is False.
    """
    success = not (record.osha_recordable_incident and not record.incident_reported)

    if not success:
        return False, ProofObject(
            rule="OSHARecordkeeping",
            premises=[
                f"record_id={record.record_id}",
                f"osha_recordable_incident={record.osha_recordable_incident}",
                f"incident_reported={record.incident_reported}",
            ],
            conclusion="VIOLATION: 29 CFR 1904 — OSHA-recordable incident not reported",
        )

    return True, ProofObject(
        rule="OSHARecordkeeping",
        premises=[
            f"record_id={record.record_id}",
            f"osha_recordable_incident={record.osha_recordable_incident}",
            f"incident_reported={record.incident_reported}",
        ],
        conclusion="29 CFR 1904 OSHA recordkeeping requirement satisfied",
    )


def check_fmla_compliance(record: WorkplaceRecord) -> Tuple[bool, ProofObject]:
    """
    Rule: FMLA-eligible employees who request leave must be granted it (FMLA 29 U.S.C. §2612).

    falsifies_if: fmla_eligible_employee AND fmla_leave_requested AND NOT fmla_leave_granted.
    """
    if record.fmla_eligible_employee and record.fmla_leave_requested:
        success = record.fmla_leave_granted
    else:
        success = True

    if not success:
        return False, ProofObject(
            rule="FMLALeaveEntitlement",
            premises=[
                f"record_id={record.record_id}",
                f"fmla_eligible_employee={record.fmla_eligible_employee}",
                f"fmla_leave_requested={record.fmla_leave_requested}",
                f"fmla_leave_granted={record.fmla_leave_granted}",
            ],
            conclusion="VIOLATION: FMLA §2612 — eligible employee's leave request denied",
        )

    return True, ProofObject(
        rule="FMLALeaveEntitlement",
        premises=[
            f"record_id={record.record_id}",
            f"fmla_eligible_employee={record.fmla_eligible_employee}",
            f"fmla_leave_requested={record.fmla_leave_requested}",
            f"fmla_leave_granted={record.fmla_leave_granted}",
        ],
        conclusion="FMLA §2612 leave entitlement satisfied",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_LABOR_RIGHTS invariants with nominal passing data.

    falsifies_if: any labor rights invariant check fails or raises an exception.
    """
    record = WorkplaceRecord(
        record_id="WR-001",
        hourly_wage=Fraction(15),
        federal_minimum_wage=Fraction(725, 100),  # $7.25
        overtime_hours=Fraction(5),
        overtime_rate_multiplier=Fraction(3, 2),
        regular_rate=Fraction(15),
        osha_recordable_incident=False,
        incident_reported=False,
        collective_bargaining_agreement=True,
        unfair_labor_practice=False,
        fmla_eligible_employee=True,
        fmla_leave_granted=True,
        fmla_leave_requested=True,
    )

    checks = [
        ("check_minimum_wage", lambda: check_minimum_wage(record)),
        ("check_overtime_rate", lambda: check_overtime_rate(record)),
        ("check_osha_recordkeeping", lambda: check_osha_recordkeeping(record)),
        ("check_fmla_compliance", lambda: check_fmla_compliance(record)),
    ]

    results: Dict[str, str] = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_LABOR_RIGHTS invariants: PASS")
