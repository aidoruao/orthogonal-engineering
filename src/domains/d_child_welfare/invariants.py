#!/usr/bin/env python3
"""D_CHILDWELFARE Invariants — CPS investigations, ASFA timelines, ICWA compliance

Child welfare per CAPTA, ASFA (1997), ICWA (1978), and state CPS regulations.
All invariants use Fraction arithmetic for exact time calculations.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    MandatoryReport, CPSInvestigation, FosterPlacement, ASFATimeline, ICWACompliance,
    InvestigationPriority, PlacementType,
    mandatory_reporting_hours, asfa_permanency_days, asfa_tpr_filing_days,
    investigation_immediate_hours, investigation_priority_hours, investigation_routine_days
)


def check_mandatory_reporting_timeline(report: MandatoryReport) -> Tuple[bool, ProofObject]:
    """
    Mandatory reporters must file within 24-48 hours (jurisdiction-dependent).

    Falsifies if: reporter_mandated AND report_filed_within_hours > 48
    """
    max_hours = mandatory_reporting_hours()

    if report.reporter_mandated and report.report_filed_within_hours > max_hours:
        return False, ProofObject(
            conclusion=f"VIOLATION: Mandatory report {report.report_id} filed after {report.report_filed_within_hours} hours (max {max_hours})",
            premises=[
                f"Reporter mandated: {report.reporter_mandated}",
                f"Filed within: {report.report_filed_within_hours} hours",
                f"Max: {max_hours} hours"
            ],
            rule="capta_mandatory_reporting"
        )

    return True, ProofObject(
        conclusion=f"Report {report.report_id} filed within required timeframe",
        premises=[f"Filed within: {report.report_filed_within_hours} hours"],
        rule="capta_mandatory_reporting"
    )


def check_cps_investigation_response_time(inv: CPSInvestigation) -> Tuple[bool, ProofObject]:
    """
    CPS investigations must meet priority-based response times.

    Falsifies if: IMMEDIATE AND hours_to_response > 24, or PRIORITY AND hours_to_response > 72
    """
    if inv.priority == InvestigationPriority.IMMEDIATE:
        max_hours = investigation_immediate_hours()
        if inv.hours_to_response > max_hours:
            return False, ProofObject(
                conclusion=f"VIOLATION: IMMEDIATE investigation {inv.investigation_id} responded in {inv.hours_to_response} hours (max {max_hours})",
                premises=[
                    f"Priority: IMMEDIATE",
                    f"Response time: {inv.hours_to_response} hours",
                    f"Max: {max_hours} hours"
                ],
                rule="cps_investigation_timeline"
            )

    if inv.priority == InvestigationPriority.PRIORITY:
        max_hours = investigation_priority_hours()
        if inv.hours_to_response > max_hours:
            return False, ProofObject(
                conclusion=f"VIOLATION: PRIORITY investigation {inv.investigation_id} responded in {inv.hours_to_response} hours (max {max_hours})",
                premises=[
                    f"Priority: PRIORITY",
                    f"Response time: {inv.hours_to_response} hours",
                    f"Max: {max_hours} hours"
                ],
                rule="cps_investigation_timeline"
            )

    if inv.priority == InvestigationPriority.ROUTINE:
        max_days = investigation_routine_days()
        max_hours = Fraction(max_days * 24, 1)
        if inv.hours_to_response > max_hours:
            return False, ProofObject(
                conclusion=f"VIOLATION: ROUTINE investigation {inv.investigation_id} responded in {inv.hours_to_response} hours (max {max_hours})",
                premises=[
                    f"Priority: ROUTINE",
                    f"Response time: {inv.hours_to_response} hours",
                    f"Max: {max_days} days = {max_hours} hours"
                ],
                rule="cps_investigation_timeline"
            )

    return True, ProofObject(
        conclusion=f"Investigation {inv.investigation_id} responded within required timeframe",
        premises=[f"Priority: {inv.priority.name}", f"Response: {inv.hours_to_response} hours"],
        rule="cps_investigation_timeline"
    )


def check_foster_placement_screening(placement: FosterPlacement) -> Tuple[bool, ProofObject]:
    """
    Foster placements require home study and background checks.

    Falsifies if: NOT (home_study_completed AND background_check_passed)
    """
    if not placement.home_study_completed or not placement.background_check_passed:
        return False, ProofObject(
            conclusion=f"VIOLATION: Placement {placement.placement_id} missing required screening",
            premises=[
                f"Home study: {placement.home_study_completed}",
                f"Background check: {placement.background_check_passed}"
            ],
            rule="foster_placement_screening"
        )

    return True, ProofObject(
        conclusion=f"Placement {placement.placement_id} meets screening requirements",
        premises=[
            f"Home study: {placement.home_study_completed}",
            f"Background check: {placement.background_check_passed}"
        ],
        rule="foster_placement_screening"
    )


def check_asfa_permanency_hearing(asfa: ASFATimeline) -> Tuple[bool, ProofObject]:
    """
    ASFA: Permanency hearing required within 12 months (365 days) of entry into care.

    Falsifies if: days_in_care > 365 AND NOT permanency_hearing_held
    """
    max_days = asfa_permanency_days()

    if asfa.days_in_care > max_days and not asfa.permanency_hearing_held:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {asfa.case_id} in care {asfa.days_in_care} days without permanency hearing (max {max_days})",
            premises=[
                f"Days in care: {asfa.days_in_care}",
                f"Permanency hearing held: {asfa.permanency_hearing_held}",
                f"ASFA deadline: {max_days} days"
            ],
            rule="asfa_permanency_hearing"
        )

    return True, ProofObject(
        conclusion=f"Case {asfa.case_id} meets ASFA permanency hearing timeline",
        premises=[f"Days in care: {asfa.days_in_care}", f"Hearing held: {asfa.permanency_hearing_held}"],
        rule="asfa_permanency_hearing"
    )


def check_asfa_tpr_filing(asfa: ASFATimeline) -> Tuple[bool, ProofObject]:
    """
    ASFA: TPR filing required if child in care 15 of last 22 months (450 days).

    Falsifies if: days_in_care > 450 AND NOT tpr_filed
    """
    max_days = asfa_tpr_filing_days()

    if asfa.days_in_care > max_days and not asfa.tpr_filed:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {asfa.case_id} in care {asfa.days_in_care} days without TPR filing (max {max_days})",
            premises=[
                f"Days in care: {asfa.days_in_care}",
                f"TPR filed: {asfa.tpr_filed}",
                f"ASFA deadline: {max_days} days (15 of 22 months)"
            ],
            rule="asfa_tpr_filing"
        )

    return True, ProofObject(
        conclusion=f"Case {asfa.case_id} meets ASFA TPR timeline",
        premises=[f"Days in care: {asfa.days_in_care}", f"TPR filed: {asfa.tpr_filed}"],
        rule="asfa_tpr_filing"
    )


def check_icwa_tribal_notification(icwa: ICWACompliance) -> Tuple[bool, ProofObject]:
    """
    ICWA: Tribes must be notified when tribal children enter foster care.

    Falsifies if: child_is_tribal_member AND NOT tribe_notified
    """
    if icwa.child_is_tribal_member and not icwa.tribe_notified:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {icwa.case_id} tribal child without tribe notification",
            premises=[
                f"Child is tribal member: {icwa.child_is_tribal_member}",
                f"Tribe notified: {icwa.tribe_notified}"
            ],
            rule="icwa_tribal_notification"
        )

    return True, ProofObject(
        conclusion=f"Case {icwa.case_id} meets ICWA tribal notification requirements",
        premises=[
            f"Tribal member: {icwa.child_is_tribal_member}",
            f"Tribe notified: {icwa.tribe_notified}"
        ],
        rule="icwa_tribal_notification"
    )


def check_icwa_active_efforts(icwa: ICWACompliance) -> Tuple[bool, ProofObject]:
    """
    ICWA: Active efforts to prevent family breakup must be documented for tribal children.

    Falsifies if: child_is_tribal_member AND NOT active_efforts_documented
    """
    if icwa.child_is_tribal_member and not icwa.active_efforts_documented:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {icwa.case_id} tribal child without documented active efforts",
            premises=[
                f"Child is tribal member: {icwa.child_is_tribal_member}",
                f"Active efforts documented: {icwa.active_efforts_documented}"
            ],
            rule="icwa_active_efforts"
        )

    return True, ProofObject(
        conclusion=f"Case {icwa.case_id} meets ICWA active efforts requirements",
        premises=[
            f"Tribal member: {icwa.child_is_tribal_member}",
            f"Active efforts: {icwa.active_efforts_documented}"
        ],
        rule="icwa_active_efforts"
    )
