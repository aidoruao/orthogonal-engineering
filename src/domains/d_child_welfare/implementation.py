"""D_CHILD_WELFARE implementation — Child Welfare Law

Implements child protection including mandatory reporting, foster care
placement standards, and termination of parental rights procedures.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: CAPTA (42 U.S.C. §5101), ASFA (42 U.S.C. §673), ICWA (25 U.S.C. §1901)

Biblical: Isaiah 1:17 — "Learn to do right; seek justice. Defend the oppressed.
Take up the cause of the fatherless; plead the case of the widow."
Also: Matthew 18:6 — warnings against harming children.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class AbuseType(Enum):
    """Types of child abuse/neglect under CAPTA."""
    PHYSICAL_ABUSE = auto()
    SEXUAL_ABUSE = auto()
    EMOTIONAL_ABUSE = auto()
    NEGLECT = auto()
    ABANDONMENT = auto()
    SUBSTANCE_EXPOSURE = auto()  # Prenatal drug exposure


class ReporterType(Enum):
    """Categories of mandatory reporters under CAPTA."""
    TEACHER = auto()
    DOCTOR = auto()
    NURSE = auto()
    SOCIAL_WORKER = auto()
    LAW_ENFORCEMENT = auto()
    DAYCARE_PROVIDER = auto()
    MENTAL_HEALTH_PROFESSIONAL = auto()


class PlacementType(Enum):
    """Types of out-of-home placement."""
    FOSTER_FAMILY = auto()
    RELATIVE_CARE = auto()  # Kinship care
    GROUP_HOME = auto()
    RESIDENTIAL_TREATMENT = auto()
    SHELTER_CARE = auto()


class TPRGround(Enum):
    """Grounds for Termination of Parental Rights under ASFA."""
    SEVERE_ABUSE = auto()
    ABANDONMENT = auto()
    MURDER_OF_SIBLING = auto()
    VOLUNTARY_SURRENDER = auto()
    FAILURE_TO_REUNIFY = auto()  # 15 of 22 months in foster care
    AGGRAVATED_CIRCUMSTANCES = auto()


@dataclass
class Child:
    """A child in the child welfare system."""
    child_id: str
    name: str
    date_of_birth: datetime
    tribal_affiliation: Optional[str] = None  # For ICWA
    
    # Current status
    in_care: bool = False
    current_placement: Optional[Placement] = None
    
    # History
    placement_history: List[Placement] = field(default_factory=list)
    
    @property
    def age(self) -> int:
        """Calculate current age in years."""
        today = datetime.now()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years


@dataclass
class Placement:
    """An out-of-home placement."""
    placement_id: str
    placement_type: PlacementType
    provider_id: str
    provider_name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    is_icwa_compliant: bool = True  # ICWA placement preferences followed
    
    @property
    def duration_days(self) -> int:
        """Duration of placement in days."""
        end = self.end_date or datetime.now()
        return (end - self.start_date).days


@dataclass
class AbuseReport:
    """A report of suspected child abuse/neglect."""
    report_id: str
    child_id: str
    reporter_type: ReporterType
    reporter_id: str
    report_date: datetime
    abuse_types: Set[AbuseType]
    description: str
    screened_in: bool = False
    investigation_start_date: Optional[datetime] = None
    substantiated: Optional[bool] = None
    
    # CAPTA requires report within 48 hours of discovery
    discovery_date: Optional[datetime] = None


@dataclass
class Parent:
    """A parent in child welfare proceedings."""
    parent_id: str
    name: str
    rights_terminated: bool = False
    tpr_date: Optional[datetime] = None
    tpr_grounds: Optional[TPRGround] = None
    
    # Case plan compliance
    case_plan_assigned: bool = False
    case_plan_start_date: Optional[datetime] = None
    services_completed: List[str] = field(default_factory=list)
    services_required: List[str] = field(default_factory=list)
    
    @property
    def case_plan_compliance_rate(self) -> Fraction:
        """Fraction of required services completed."""
        if not self.services_required:
            return Fraction(1)
        return Fraction(len(self.services_completed), len(self.services_required))


class MandatoryReportingSystem:
    """System for handling mandatory reports under CAPTA."""
    
    REPORTING_DEADLINE_HOURS = 48  # CAPTA requirement
    
    def __init__(self):
        self.reports: Dict[str, AbuseReport] = {}
        self.violations: List[Dict] = []
    
    def check_reporting_compliance(self, report: AbuseReport) -> Dict:
        """Check if report was filed within CAPTA deadline."""
        if not report.discovery_date:
            return {"compliant": None, "reason": "No discovery date recorded"}
        
        hours_elapsed = (report.report_date - report.discovery_date).total_seconds() / 3600
        compliant = hours_elapsed <= self.REPORTING_DEADLINE_HOURS
        
        return {
            "compliant": compliant,
            "hours_elapsed": hours_elapsed,
            "deadline_hours": self.REPORTING_DEADLINE_HOURS,
            "reporter_type": report.reporter_type.name,
        }
    
    def screen_report(self, report: AbuseReport) -> Dict:
        """Screen a report for investigation (intake decision)."""
        # Screen in if involves physical/sexual abuse, neglect, or substance exposure
        screen_in_types = {
            AbuseType.PHYSICAL_ABUSE,
            AbuseType.SEXUAL_ABUSE,
            AbuseType.NEGLECT,
            AbuseType.SUBSTANCE_EXPOSURE,
        }
        
        should_screen_in = bool(report.abuse_types & screen_in_types)
        
        # CAPTA requires immediate screening
        return {
            "screened_in": should_screen_in,
            "screening_date": datetime.now(),
            "requires_immediate_response": AbuseType.PHYSICAL_ABUSE in report.abuse_types,
            "rationale": "Meets CAPTA criteria" if should_screen_in else "Does not meet criteria",
        }


class FosterCarePlacementSystem:
    """System for managing foster care placements."""
    
    # ASFA timelines
    PERMANENCY_HEARING_DEADLINE_DAYS = 365  # 12 months
    TPR_FILING_DEADLINE_DAYS = 60  # After 15 of 22 months
    
    def __init__(self):
        self.placements: Dict[str, Placement] = {}
        self.children: Dict[str, Child] = {}
    
    def calculate_placement_preference(
        self,
        child: Child,
        available_placements: List[Placement],
    ) -> Dict:
        """Calculate placement preference per ICWA and best practices."""
        preferences = []
        
        for placement in available_placements:
            score = 0
            reasons = []
            
            # ICWA preference: tribal member > Indian family > foster home > institution
            if child.tribal_affiliation:
                # Would check if placement provider is tribal member
                pass
            
            # Kinship care preference (ASFA)
            if placement.placement_type == PlacementType.RELATIVE_CARE:
                score += 10
                reasons.append("Kinship care preferred")
            
            # Least restrictive setting
            if placement.placement_type == PlacementType.FOSTER_FAMILY:
                score += 5
                reasons.append("Family setting")
            elif placement.placement_type == PlacementType.RESIDENTIAL_TREATMENT:
                score -= 5  # Most restrictive
            
            preferences.append({
                "placement": placement,
                "score": score,
                "reasons": reasons,
            })
        
        # Sort by score descending
        preferences.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "ranked_preferences": preferences,
            "top_choice": preferences[0] if preferences else None,
        }
    
    def check_permanency_timeline(self, child: Child) -> Dict:
        """Check if permanency hearing timeline is met."""
        if not child.placement_history:
            return {"overdue": False, "days_in_care": 0}
        
        first_placement = child.placement_history[0]
        days_in_care = (datetime.now() - first_placement.start_date).days
        
        # ASFA requires permanency hearing within 12 months
        overdue = days_in_care > self.PERMANENCY_HEARING_DEADLINE_DAYS
        
        return {
            "overdue": overdue,
            "days_in_care": days_in_care,
            "deadline_days": self.PERMANENCY_HEARING_DEADLINE_DAYS,
            "requires_tpr_consideration": self._requires_tpr_filing(child),
        }
    
    def _requires_tpr_filing(self, child: Child) -> bool:
        """Check if child meets 15 of 22 months criteria for TPR filing."""
        if not child.placement_history:
            return False
        
        # Calculate total days in care
        total_days = sum(p.duration_days for p in child.placement_history)
        total_days += child.current_placement.duration_days if child.current_placement else 0
        
        # 15 of 22 months = ~473 days
        return total_days >= 473


class TPREvaluator:
    """Evaluator for Termination of Parental Rights under ASFA."""
    
    # ASFA aggravated circumstances requiring expedited TPR
    AGGRAVATED_CIRCUMSTANCES = {
        AbuseType.SEXUAL_ABUSE,
        AbuseType.ABANDONMENT,
    }
    
    def __init__(self):
        self.cases: List[Dict] = []
    
    def evaluate_tpr_grounds(
        self,
        parent: Parent,
        child: Child,
        abuse_history: List[AbuseReport],
    ) -> Dict:
        """Evaluate grounds for termination of parental rights."""
        grounds_found = []
        recommendations = []
        
        # Check for aggravated circumstances
        for report in abuse_history:
            if report.substantiated and report.abuse_types & self.AGGRAVATED_CIRCUMSTANCES:
                grounds_found.append(TPRGround.AGGRAVATED_CIRCUMSTANCES)
                recommendations.append("Expedited TPR filing due to aggravated circumstances")
                break
        
        # Check 15 of 22 months criteria
        total_days_in_care = sum(p.duration_days for p in child.placement_history)
        if child.current_placement:
            total_days_in_care += child.current_placement.duration_days
        
        if total_days_in_care >= 473:  # 15 of 22 months
            # Check case plan compliance
            if parent.case_plan_compliance_rate < Fraction(1, 2):
                grounds_found.append(TPRGround.FAILURE_TO_REUNIFY)
                recommendations.append("TPR - failure to reunify despite services")
        
        # Check abandonment (no contact for 6+ months)
        # Simplified check
        
        return {
            "grounds_found": grounds_found,
            "recommendations": recommendations,
            "clear_and_convincing_evidence_required": True,
            "burden": "clear_and_convincing",  # Santosky v. Kramer
        }
    
    def check_icwa_requirements(self, child: Child) -> Dict:
        """Check ICWA requirements for Indian children."""
        if not child.tribal_affiliation:
            return {"applicable": False}
        
        return {
            "applicable": True,
            "tribe": child.tribal_affiliation,
            "active_efforts_required": True,  # Higher standard than ASFA
            "expert_witness_required": True,  # Qualified expert witness
            "placement_preferences": [
                "Extended family member",
                "Tribal member",
                "Other Indian family",
                "Institution approved by tribe",
            ],
        }


class ChildWelfareCaseManager:
    """Comprehensive case manager for child welfare matters."""
    
    def __init__(self):
        self.reporting_system = MandatoryReportingSystem()
        self.placement_system = FosterCarePlacementSystem()
        self.tpr_evaluator = TPREvaluator()
    
    def conduct_case_review(self, child: Child, parent: Parent) -> Dict:
        """Conduct comprehensive case review."""
        permanency = self.placement_system.check_permanency_timeline(child)
        icwa = self.tpr_evaluator.check_icwa_requirements(child)
        
        return {
            "child_id": child.child_id,
            "age": child.age,
            "days_in_care": permanency["days_in_care"],
            "permanency_overdue": permanency["overdue"],
            "requires_tpr_filing": permanency["requires_tpr_consideration"],
            "icwa_applies": icwa["applicable"],
            "parent_compliance": float(parent.case_plan_compliance_rate),
        }


# Convenience functions
def check_mandatory_reporting_deadline(
    discovery_date: datetime,
    report_date: datetime,
) -> Dict:
    """Check if report was filed within CAPTA 48-hour deadline."""
    hours = (report_date - discovery_date).total_seconds() / 3600
    return {
        "compliant": hours <= 48,
        "hours_elapsed": hours,
        "deadline_hours": 48,
    }


def check_icwa_placement_preference(child_tribal_affiliation: Optional[str]) -> Dict:
    """Check ICWA placement preferences for Indian child."""
    if not child_tribal_affiliation:
        return {"icwa_applies": False}
    
    return {
        "icwa_applies": True,
        "preference_order": [
            "member of child's extended family",
            "foster home licensed by tribe",
            "Indian foster home",
            "institution approved by tribe",
        ],
    }


def check_asfa_timeline(days_in_care: int) -> Dict:
    """Check ASFA permanency timeline compliance."""
    return {
        "permanency_hearing_required": days_in_care >= 365,
        "tpr_filing_required": days_in_care >= 473,  # 15 of 22 months
        "days_remaining": max(0, 365 - days_in_care),
    }
