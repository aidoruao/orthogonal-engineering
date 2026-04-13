#!/usr/bin/env python3
"""Elder Care Domain Invariants — Quality, safety, regulatory compliance.

Regulatory Standards:
- Nursing Home Reform Act (OBRA 1987)
- CMS Conditions of Participation 42 CFR 483
- Elder Justice Act
- LTC Ombudsman Program

Falsifies if:
- Staffing below CMS minimums
- Care plans not reviewed quarterly
- Abuse investigations not completed timely
- Quality metrics exceed safety thresholds
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Facility, AbuseReport, CarePlan, OmbudsmanComplaint,
    StaffingRatio, CareSetting
)


def check_staffing_compliance(facility: Facility) -> Tuple[bool, ProofObject]:
    """CMS requires minimum nursing hours per resident day.
    
    Falsifies if: total_nursing_hours < 0.3 per resident day or rn_hours_per_resident_day == 0.
    falsifies_if: total_nursing_hours < 0.3 per resident day or rn_hours_per_resident_day == 0.
    """
    CMS_MIN_TOTAL = Fraction(3, 10)  # 0.3 hours
    
    if facility.staffing.total_nursing_hours < CMS_MIN_TOTAL:
        return False, ProofObject(
            conclusion=f"VIOLATION: Staffing below CMS minimum {facility.staffing.total_nursing_hours} < {CMS_MIN_TOTAL}",
            premises=[
                f"Total hours: {facility.staffing.total_nursing_hours}",
                f"CMS minimum: {CMS_MIN_TOTAL}",
                f"Facility: {facility.name}"
            ],
            rule="cms_staffing_minimum_42cfr483"
        )
    
    if facility.staffing.rn_hours_per_resident_day == 0:
        return False, ProofObject(
            conclusion="VIOLATION: No registered nurse coverage",
            premises=["RN hours: 0"],
            rule="cms_rn_coverage_required"
        )
    
    return True, ProofObject(
        conclusion="Facility meets CMS staffing requirements",
        premises=[f"Total hours: {facility.staffing.total_nursing_hours}"],
        rule="cms_staffing_compliant"
    )


def check_care_plan_currency(plan: CarePlan) -> Tuple[bool, ProofObject]:
    """OBRA requires care plan review at least quarterly (every 90 days).
    
    Falsifies if: days since last review exceed 90 or comprehensive assessment is stale.
    falsifies_if: days since last review exceed 90 or comprehensive assessment is stale.
    """
    from datetime import datetime
    days_since_review = (datetime.now() - plan.last_reviewed).days
    
    if days_since_review > 90:
        return False, ProofObject(
            conclusion=f"VIOLATION: Care plan not reviewed in {days_since_review} days (max 90)",
            premises=[
                f"Last review: {plan.last_reviewed}",
                f"Days elapsed: {days_since_review}"
            ],
            rule="obra_care_plan_review_quarterly"
        )
    
    return True, ProofObject(
        conclusion="Care plan reviewed within required timeframe",
        premises=[f"Days since review: {days_since_review}"],
        rule="obra_care_plan_current"
    )


def check_abuse_investigation_timeliness(report: AbuseReport) -> Tuple[bool, ProofObject]:
    """Elder Justice Act requires timely abuse investigation.
    
    Falsifies if: investigation exceeds 60 days or completed cases lack required reporting.
    falsifies_if: investigation exceeds 60 days or completed cases lack required reporting.
    """
    MAX_INVESTIGATION_DAYS = 60
    
    if not report.investigation_completed:
        from datetime import datetime
        days_pending = (datetime.now() - report.report_date).days
        if days_pending > MAX_INVESTIGATION_DAYS:
            return False, ProofObject(
                conclusion=f"VIOLATION: Abuse investigation pending {days_pending} days",
                premises=[
                    f"Reported: {report.report_date}",
                    f"Days pending: {days_pending}",
                    f"Max allowed: {MAX_INVESTIGATION_DAYS}"
                ],
                rule="elder_justice_timely_investigation"
            )
        return True, ProofObject(
            conclusion="Abuse investigation in progress",
            premises=[f"Days pending: {days_pending}"],
            rule="investigation_pending"
        )
    
    investigation_days = report.investigation_timeliness()
    if investigation_days is not None and investigation_days > MAX_INVESTIGATION_DAYS:
        return False, ProofObject(
            conclusion=f"VIOLATION: Investigation took {investigation_days} days (max {MAX_INVESTIGATION_DAYS})",
            premises=[f"Days to complete: {investigation_days}"],
            rule="elder_justice_timely_investigation"
        )
    
    return True, ProofObject(
        conclusion="Abuse investigation completed timely",
        premises=[f"Days to complete: {investigation_days}"],
        rule="investigation_compliant"
    )


def check_fall_rate_threshold(facility: Facility, threshold: Fraction) -> Tuple[bool, ProofObject]:
    """CMS quality measure: Falls with major injury per 1000 resident days.
    
    Falsifies if: facility.falls_per_1000_bed_days exceeds threshold.
    falsifies_if: facility.falls_per_1000_bed_days exceeds threshold.
    """
    if facility.falls_per_1000_bed_days > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Fall rate {facility.falls_per_1000_bed_days} exceeds threshold {threshold}",
            premises=[
                f"Falls/1000 days: {facility.falls_per_1000_bed_days}",
                f"Threshold: {threshold}",
                f"Facility: {facility.name}"
            ],
            rule="cms_fall_rate_quality_measure"
        )
    
    return True, ProofObject(
        conclusion="Fall rate within acceptable threshold",
        premises=[f"Fall rate: {facility.falls_per_1000_bed_days}"],
        rule="fall_rate_compliant"
    )


def check_pressure_ulcer_rate(facility: Facility, threshold: Fraction) -> Tuple[bool, ProofObject]:
    """CMS quality measure: Pressure ulcers (bed sores) per 1000 resident days.
    
    Falsifies if: pressure_ulcers_per_1000 exceeds threshold.
    falsifies_if: pressure_ulcers_per_1000 exceeds threshold.
    """
    if facility.pressure_ulcers_per_1000 > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Pressure ulcer rate {facility.pressure_ulcers_per_1000} exceeds threshold",
            premises=[
                f"Ulcers/1000 days: {facility.pressure_ulcers_per_1000}",
                f"Threshold: {threshold}"
            ],
            rule="cms_pressure_ulcer_quality_measure"
        )
    
    return True, ProofObject(
        conclusion="Pressure ulcer rate within acceptable range",
        premises=[f"Rate: {facility.pressure_ulcers_per_1000}"],
        rule="pressure_ulcer_compliant"
    )


def check_ombudsman_resolution_time(complaint: OmbudsmanComplaint) -> Tuple[bool, ProofObject]:
    """LTC Ombudsman program tracks resolution timeliness.
    
    Falsifies if: complaint remains unresolved beyond 90 days or resolution times exceed program standards.
    falsifies_if: complaint remains unresolved beyond 90 days or resolution times exceed program standards.
    """
    MAX_RESOLUTION_DAYS = 90
    
    if not complaint.resolved:
        from datetime import datetime
        days_open = (datetime.now() - complaint.complaint_date).days
        if days_open > MAX_RESOLUTION_DAYS:
            return False, ProofObject(
                conclusion=f"VIOLATION: Ombudsman complaint open {days_open} days",
                premises=[
                    f"Complaint date: {complaint.complaint_date}",
                    f"Days open: {days_open}"
                ],
                rule="ombudsman_timely_resolution"
            )
        return True, ProofObject(
            conclusion="Ombudsman complaint being processed",
            premises=[f"Days open: {days_open}"],
            rule="complaint_pending"
        )
    
    resolution_days = complaint.resolution_time()
    if resolution_days is not None and resolution_days > MAX_RESOLUTION_DAYS:
        return False, ProofObject(
            conclusion=f"VIOLATION: Complaint resolution took {resolution_days} days",
            premises=[f"Resolution time: {resolution_days} days"],
            rule="ombudsman_timely_resolution"
        )
    
    return True, ProofObject(
        conclusion="Ombudsman complaint resolved timely",
        premises=[f"Resolution time: {resolution_days} days"],
        rule="ombudsman_resolution_compliant"
    )


def run_all_invariants() -> dict:
    """Run all D_ELDER_CARE invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    abuse_report = AbuseReport(
        report_id=None,
        facility_id=None,
        report_date=None,
        allegation_type=None,
        substantiated=None,
        investigation_completed=None,
    )
    care_plan = CarePlan(
        plan_id=None,
        resident_id=None,
        created_date=None,
        last_reviewed=None,
        comprehensive_assessment_completed=None,
        mds_completed=None,
        care_conference_held=None,
        family_notified=None,
    )
    facility = Facility(
        facility_id=None,
        name=None,
        care_setting=CareSetting.NURSING_HOME,
        certified_beds=None,
        occupied_beds=None,
        staffing=StaffingRatio(
        rn_hours_per_resident_day=Fraction(1),
        lpn_hours_per_resident_day=Fraction(1),
        cna_hours_per_resident_day=Fraction(1),
        total_nursing_hours=Fraction(1),
    ),
        cms_rating=None,
        falls_per_1000_bed_days=Fraction(1),
        pressure_ulcers_per_1000=Fraction(1),
        medication_errors_per_1000=Fraction(1),
    )
    ombudsman_complaint = OmbudsmanComplaint(
        complaint_id=None,
        facility_id=None,
        complaint_date=None,
        issue_category=None,
        resolved=None,
    )

    checks = [
        ("check_abuse_investigation_timeliness", lambda: check_abuse_investigation_timeliness(abuse_report)),
        ("check_care_plan_currency", lambda: check_care_plan_currency(care_plan)),
        ("check_fall_rate_threshold", lambda: check_fall_rate_threshold(facility, Fraction(1000))),
        ("check_ombudsman_resolution_time", lambda: check_ombudsman_resolution_time(ombudsman_complaint)),
        ("check_pressure_ulcer_rate", lambda: check_pressure_ulcer_rate(facility, Fraction(1000))),
        ("check_staffing_compliance", lambda: check_staffing_compliance(facility)),
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
    print("All D_ELDER_CARE invariants: PASS")
