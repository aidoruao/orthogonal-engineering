"""D_CHILDWELFARE implementation — Child Welfare and Social Services

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE

Child welfare covers CPS investigations, mandatory reporting, ASFA timelines, and ICWA compliance.
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum
from typing import Optional


class InvestigationPriority(Enum):
    """CPS investigation priority levels"""
    IMMEDIATE = 1  # <24 hours
    PRIORITY = 2   # <72 hours
    ROUTINE = 3    # <10 days


class PlacementType(Enum):
    """Foster care placement categories"""
    KINSHIP = 1
    FOSTER_HOME = 2
    GROUP_HOME = 3
    RESIDENTIAL = 4


@dataclass
class MandatoryReport:
    """Mandatory abuse/neglect report"""
    report_id: str
    reporter_mandated: bool
    report_filed_within_hours: Fraction
    jurisdiction: str


@dataclass
class CPSInvestigation:
    """Child Protective Services investigation"""
    investigation_id: str
    priority: InvestigationPriority
    hours_to_response: Fraction
    substantiated: bool


@dataclass
class FosterPlacement:
    """Foster care placement record"""
    placement_id: str
    child_age_years: Fraction
    placement_type: PlacementType
    home_study_completed: bool
    background_check_passed: bool


@dataclass
class ASFATimeline:
    """Adoption and Safe Families Act timeline"""
    case_id: str
    days_in_care: int
    permanency_hearing_held: bool
    tpr_filed: bool  # Termination of Parental Rights


@dataclass
class ICWACompliance:
    """Indian Child Welfare Act compliance"""
    case_id: str
    child_is_tribal_member: bool
    tribe_notified: bool
    active_efforts_documented: bool


def mandatory_reporting_hours() -> Fraction:
    """Mandatory reporters must file within 24-48 hours (jurisdiction-dependent)"""
    return Fraction(48, 1)


def asfa_permanency_days() -> int:
    """ASFA: permanency hearing required within 12 months (365 days)"""
    return 365


def asfa_tpr_filing_days() -> int:
    """ASFA: TPR filing required if in care 15 of last 22 months (450 days)"""
    return 450


def investigation_immediate_hours() -> Fraction:
    """IMMEDIATE priority: response within 24 hours"""
    return Fraction(24, 1)


def investigation_priority_hours() -> Fraction:
    """PRIORITY: response within 72 hours"""
    return Fraction(72, 1)


def investigation_routine_days() -> int:
    """ROUTINE: response within 10 days"""
    return 10
