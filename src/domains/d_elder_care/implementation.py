"""D_ELDER_CARE implementation — Elder Care & Long-Term Services

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Regulatory Standards:
- Nursing Home Reform Act (OBRA 1987) 42 U.S.C. 1395i-3
- CMS Conditions of Participation 42 CFR 483
- Elder Justice Act 42 U.S.C. 1397j
- Adult Protective Services (state laws)
- Long-Term Care Ombudsman Program 42 U.S.C. 3058g
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class CareSetting(Enum):
    """Settings for long-term care."""
    NURSING_HOME = auto()
    ASSISTED_LIVING = auto()
    HOME_HEALTH = auto()
    ADULT_DAY = auto()
    HOSPICE = auto()
    MEMORY_CARE = auto()


class CareNeedLevel(Enum):
    """Level of care needs."""
    INDEPENDENT = auto()
    ASSISTED = auto()
    SKILLED = auto()
    SPECIALIZED = auto()  # Dementia, ventilator, etc.


@dataclass(frozen=True)
class StaffingRatio:
    """CMS staffing ratio requirements per resident day."""
    rn_hours_per_resident_day: Fraction
    lpn_hours_per_resident_day: Fraction
    cna_hours_per_resident_day: Fraction
    total_nursing_hours: Fraction
    
    def meets_cms_minimum(self) -> bool:
        """CMS requires minimum nursing hours per resident day."""
        CMS_MIN_TOTAL = Fraction(3, 10)  # 0.3 hours minimum (varies by state)
        return self.total_nursing_hours >= CMS_MIN_TOTAL


@dataclass
class Resident:
    """Long-term care resident."""
    resident_id: str
    admission_date: datetime
    care_setting: CareSetting
    care_level: CareNeedLevel
    has_dementia: bool
    requires_lift_assist: bool
    fall_risk: bool
    pressure_injury_risk: bool
    medications_count: int
    
    def length_of_stay_days(self) -> int:
        """Days since admission."""
        return (datetime.now() - self.admission_date).days
    
    def is_high_acuity(self) -> bool:
        """Requires specialized care."""
        return self.care_level == CareNeedLevel.SPECIALIZED or self.has_dementia


@dataclass
class Facility:
    """Long-term care facility."""
    facility_id: str
    name: str
    care_setting: CareSetting
    certified_beds: int
    occupied_beds: int
    staffing: StaffingRatio
    cms_rating: int  # 1-5 stars
    
    # Quality metrics
    falls_per_1000_bed_days: Fraction
    pressure_ulcers_per_1000: Fraction
    medication_errors_per_1000: Fraction
    
    deficiency_citations: List[str] = field(default_factory=list)
    residents: List[Resident] = field(default_factory=list)
    
    def occupancy_rate(self) -> Fraction:
        """Current occupancy as fraction."""
        if self.certified_beds == 0:
            return Fraction(0)
        return Fraction(self.occupied_beds, self.certified_beds)
    
    def available_beds(self) -> int:
        """Unoccupied beds."""
        return self.certified_beds - self.occupied_beds
    
    def is_fully_staffed(self) -> bool:
        """Meets CMS staffing requirements."""
        return self.staffing.meets_cms_minimum()


@dataclass
class AbuseReport:
    """Elder abuse or neglect report."""
    report_id: str
    facility_id: Optional[str]
    report_date: datetime
    allegation_type: str  # physical, emotional, financial, neglect, sexual
    substantiated: Optional[bool]  # None if pending
    investigation_completed: bool
    investigation_completion_date: Optional[datetime] = None
    
    def investigation_timeliness(self) -> Optional[int]:
        """Days to complete investigation."""
        if not self.investigation_completed or self.investigation_completion_date is None:
            return None
        return (self.investigation_completion_date - self.report_date).days


@dataclass
class CarePlan:
    """Resident-centered care plan per OBRA 1987."""
    plan_id: str
    resident_id: str
    created_date: datetime
    last_reviewed: datetime
    
    # Required assessments
    comprehensive_assessment_completed: bool
    mds_completed: bool  # Minimum Data Set
    care_conference_held: bool
    family_notified: bool
    
    goals: List[str] = field(default_factory=list)
    interventions: List[str] = field(default_factory=list)
    
    def is_current(self) -> bool:
        """Care plan reviewed within required timeframe."""
        days_since_review = (datetime.now() - self.last_reviewed).days
        
        # MDS comprehensive assessment required annually
        # Care plan review required quarterly
        return days_since_review <= 90
    
    def completeness_score(self) -> Fraction:
        """Fraction of required components present."""
        required = [
            self.comprehensive_assessment_completed,
            self.mds_completed,
            self.care_conference_held,
            len(self.goals) > 0,
            len(self.interventions) > 0
        ]
        return Fraction(sum(required), len(required))


@dataclass
class OmbudsmanComplaint:
    """Long-Term Care Ombudsman complaint."""
    complaint_id: str
    facility_id: str
    complaint_date: datetime
    issue_category: str
    resolved: bool
    resolution_date: Optional[datetime] = None
    resolution_days: Optional[int] = None
    
    def resolution_time(self) -> Optional[int]:
        """Days to resolution."""
        if self.resolved and self.resolution_date:
            return (self.resolution_date - self.complaint_date).days
        return None


@dataclass
class ElderCareChecker:
    """Checker for elder care quality and compliance."""
    facilities: List[Facility] = field(default_factory=list)
    abuse_reports: List[AbuseReport] = field(default_factory=list)
    care_plans: List[CarePlan] = field(default_factory=list)
    complaints: List[OmbudsmanComplaint] = field(default_factory=list)
    
    def underperforming_facilities(self, threshold: Fraction) -> List[Facility]:
        """Facilities with quality metrics above threshold."""
        return [f for f in self.facilities if f.falls_per_1000_bed_days > threshold]
    
    def pending_abuse_investigations(self) -> List[AbuseReport]:
        """Reports awaiting investigation completion."""
        return [r for r in self.abuse_reports if not r.investigation_completed]
    
    def outdated_care_plans(self) -> List[CarePlan]:
        """Care plans requiring review."""
        return [p for p in self.care_plans if not p.is_current()]
    
    def substantiated_abuse_rate(self) -> Fraction:
        """Fraction of investigated reports that were substantiated."""
        investigated = [r for r in self.abuse_reports if r.substantiated is not None]
        if not investigated:
            return Fraction(0)
        substantiated = sum(1 for r in investigated if r.substantiated)
        return Fraction(substantiated, len(investigated))
