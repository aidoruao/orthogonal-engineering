"""D_EMPLOYMENT_LAW implementation — Employment Law

Implements employment law including Title VII (discrimination), ADA
(accommodations), ADEA (age), FMLA (leave), and wage/hour requirements.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: 42 U.S.C. §2000e (Title VII), 42 U.S.C. §12101 (ADA),
        29 U.S.C. §621 (ADEA), 29 U.S.C. §2601 (FMLA)

Imports from D_LABOR_RIGHTS: NLRA rights apply to non-supervisory employees.

Biblical: James 5:4 — "Look! The wages you failed to pay the workers
who mowed your fields are crying out against you. The cries of the
harvesters have reached the ears of the Lord Almighty."

Also: Leviticus 19:13 — "Do not hold back the wages of a hired worker
overnight."

Also: Deuteronomy 24:14-15 — "Do not take advantage of a hired worker
who is poor and needy... Pay them their wages each day before sunset."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction

# Import from D_LABOR_RIGHTS where applicable
try:
    from src.domains.d_labor_rights import NLRAProtectedActivity
    HAS_LABOR_RIGHTS = True
except ImportError:
    HAS_LABOR_RIGHTS = False


class ProtectedClass(Enum):
    """Protected classes under Title VII, ADA, and related statutes."""
    RACE = auto()           # Title VII
    COLOR = auto()          # Title VII
    RELIGION = auto()       # Title VII - includes accommodation
    SEX = auto()            # Title VII - includes pregnancy, sexual orientation
    NATIONAL_ORIGIN = auto()  # Title VII
    AGE = auto()            # ADEA (40+)
    DISABILITY = auto()     # ADA
    GENETIC_INFORMATION = auto()  # GINA


class EmploymentActionType(Enum):
    """Types of employment actions."""
    HIRING = auto()
    PROMOTION = auto()
    DEMOTION = auto()
    TERMINATION = auto()
    LAYOFF = auto()
    PAY_ADJUSTMENT = auto()
    SCHEDULE_CHANGE = auto()
    DISCIPLINE = auto()


class FMLAQualifyingReason(Enum):
    """FMLA qualifying reasons for leave."""
    BIRTH_OF_CHILD = auto()
    ADOPTION_FOSTER = auto()
    SERIOUS_HEALTH_CONDITION_SELF = auto()
    SERIOUS_HEALTH_CONDITION_FAMILY = auto()
    MILITARY_EXIGENCY = auto()
    MILITARY_CAREGIVER = auto()


class DischargeCategory(Enum):
    """Categories of employment discharge."""
    VOLUNTARY = auto()
    MISCONDUCT = auto()
    PERFORMANCE = auto()
    LAYOFF_LACK_OF_WORK = auto()
    DISCRIMINATION = auto()
    RETALIATION = auto()


@dataclass
class Employee:
    """An employee for employment law analysis."""
    employee_id: str
    name: str
    hire_date: datetime
    
    # Protected characteristics
    protected_classes: Set[ProtectedClass] = field(default_factory=set)
    age: Optional[int] = None
    has_disability: bool = False
    religion_accommodation_needed: Optional[str] = None
    
    # Employment status
    is_supervisory: bool = False
    full_time: bool = True
    hourly_rate: Optional[Fraction] = None
    salary: Optional[Fraction] = None
    
    # FMLA eligibility
    hours_worked_last_12_months: int = 0
    fmla_leave_taken: int = 0  # Days
    
    # History
    performance_reviews: List[Dict] = field(default_factory=list)
    complaints_filed: List[str] = field(default_factory=list)
    
    @property
    def years_of_service(self) -> float:
        """Years of service."""
        delta = datetime.now() - self.hire_date
        return delta.days / 365.25
    
    @property
    def meets_fmla_hours(self) -> bool:
        """Check if employee meets FMLA hours requirement (1,250 hours)."""
        return self.hours_worked_last_12_months >= 1250
    
    @property
    def fmla_eligible(self) -> bool:
        """Check full FMLA eligibility."""
        # 12 months employment + 1,250 hours + 50+ employees at employer
        return (
            self.years_of_service >= 1 and
            self.meets_fmla_hours
        )
    
    @property
    def fmla_remaining(self) -> int:
        """FMLA leave days remaining (12 weeks = 60 work days)."""
        max_days = 60  # 12 weeks * 5 days
        return max(0, max_days - self.fmla_leave_taken)


@dataclass
class EmploymentAction:
    """An employment action affecting an employee."""
    action_id: str
    employee: Employee
    action_type: EmploymentActionType
    action_date: datetime
    
    # Decision makers
    decision_maker: str = ""
    decision_reason: str = ""
    
    # Comparative data
    comparator_employees: List[str] = field(default_factory=list)
    
    # Timing (for retaliation analysis)
    protected_activity_date: Optional[datetime] = None
    days_since_protected_activity: Optional[int] = None
    
    def __post_init__(self):
        """Calculate days since protected activity."""
        if self.protected_activity_date and self.days_since_protected_activity is None:
            delta = self.action_date - self.protected_activity_date
            self.days_since_protected_activity = delta.days


@dataclass
class DiscriminationClaim:
    """An employment discrimination claim."""
    claim_id: str
    employee: Employee
    adverse_action: EmploymentAction
    protected_class: ProtectedClass
    
    # Evidence
    comparator_treatment: List[Dict] = field(default_factory=list)
    direct_evidence: List[str] = field(default_factory=list)
    circumstantial_evidence: List[str] = field(default_factory=list)
    
    # Statistics
    adverse_impact_statistics: Optional[Dict] = None
    
    def has_prima_facie_case(self) -> bool:
        """Check if claim states prima facie case under McDonnell Douglas.
        
        1. Member of protected class
        2. Qualified for position
        3. Subject to adverse action
        4. Similarly situated non-protected treated better
        """
        return (
            self.protected_class in self.employee.protected_classes and
            len(self.adverse_action.decision_reason) > 0 and
            len(self.comparator_treatment) > 0
        )


@dataclass
class AccommodationRequest:
    """ADA or religious accommodation request."""
    request_id: str
    employee: Employee
    accommodation_type: str  # "ADA" or "RELIGIOUS"
    
    # Request details
    requested_accommodation: str
    disability_or_religion: str
    
    # Interactive process
    medical_documentation: bool = False
    employer_response: Optional[str] = None
    accommodation_granted: Optional[bool] = None
    alternative_offered: Optional[str] = None
    
    # Undue hardship analysis
    cost_estimate: Optional[Fraction] = None
    operational_impact: Optional[str] = None
    
    def interactive_process_followed(self) -> bool:
        """Check if interactive process was followed."""
        return (
            self.employer_response is not None and
            (self.accommodation_granted is not None or self.alternative_offered is not None)
        )


class TitleVIIAnalyzer:
    """Analyzer for Title VII discrimination claims.
    
    Title VII prohibits discrimination based on race, color, religion,
    sex, or national origin in employment decisions.
    """
    
    def __init__(self):
        self.disparate_impact_threshold = Fraction(4, 5)  # 80% rule
    
    def analyze_discrimination_claim(self, claim: DiscriminationClaim) -> Dict:
        """Analyze discrimination claim under Title VII.
        
        Framework:
        1. Prima facie case (McDonnell Douglas)
        2. Legitimate non-discriminatory reason
        3. Pretext (if LNDR provided)
        """
        analysis = {
            "claim_id": claim.claim_id,
            "prima_facie": claim.has_prima_facie_case(),
            "disparate_treatment": False,
            "disparate_impact": False,
            "recommendation": "INSUFFICIENT_EVIDENCE",
        }
        
        if not analysis["prima_facie"]:
            return analysis
        
        # Check for direct evidence
        if claim.direct_evidence:
            analysis["disparate_treatment"] = True
            analysis["recommendation"] = "REASONABLE_CAUSE"
            return analysis
        
        # Check comparator treatment
        better_treatment = [
            c for c in claim.comparator_treatment
            if c.get("similarly_situated") and not c.get("adverse_action")
        ]
        
        if better_treatment:
            analysis["disparate_treatment"] = True
            analysis["recommendation"] = "REASONABLE_CAUSE"
        
        # Check for retaliation timing
        if (claim.adverse_action.days_since_protected_activity is not None and
            claim.adverse_action.days_since_protected_activity <= 90):
            analysis["retaliation_suspected"] = True
        
        return analysis
    
    def analyze_disparate_impact(
        self,
        selection_rate_protected: Fraction,
        selection_rate_non_protected: Fraction,
    ) -> Dict:
        """Analyze for disparate impact using 80% rule.
        
        If protected group selection rate is less than 80% of
        non-protected rate, disparate impact may exist.
        """
        if selection_rate_non_protected == 0:
            return {"disparate_impact": False, "ratio": None}
        
        ratio = selection_rate_protected / selection_rate_non_protected
        
        return {
            "disparate_impact": ratio < self.disparate_impact_threshold,
            "ratio": ratio,
            "protected_rate": selection_rate_protected,
            "non_protected_rate": selection_rate_non_protected,
            "threshold": self.disparate_impact_threshold,
        }


class ADAAccommodationAnalyzer:
    """Analyzer for ADA accommodation requirements.
    
    ADA requires reasonable accommodation for qualified individuals
    with disabilities, absent undue hardship.
    """
    
    def analyze_accommodation_request(self, request: AccommodationRequest) -> Dict:
        """Analyze accommodation request.
        
        Framework:
        1. Does employee have disability?
        2. Is accommodation reasonable?
        3. Would it cause undue hardship?
        """
        analysis = {
            "request_id": request.request_id,
            "has_disability": request.employee.has_disability,
            "qualified": True,  # Presumed qualified
            "interactive_process_followed": request.interactive_process_followed(),
            "accommodation_reasonable": None,
            "undue_hardship": False,
            "required": False,
        }
        
        if not analysis["has_disability"]:
            analysis["reason"] = "No qualifying disability"
            return analysis
        
        # Check if interactive process followed
        if not analysis["interactive_process_followed"]:
            analysis["violation"] = "FAILURE_TO_ENGAGE"
            return analysis
        
        # Analyze undue hardship
        if request.cost_estimate:
            # Cost exceeding certain threshold may be undue hardship
            if request.cost_estimate > Fraction(50000):  # Simplified threshold
                analysis["undue_hardship"] = True
        
        analysis["accommodation_reasonable"] = not analysis["undue_hardship"]
        analysis["required"] = (
            analysis["has_disability"] and
            analysis["accommodation_reasonable"] and
            request.accommodation_granted is not True
        )
        
        return analysis


class FMLAEligibilityChecker:
    """Checker for FMLA eligibility and compliance.
    
    FMLA provides 12 weeks unpaid leave for qualifying reasons.
    """
    
    MAX_LEAVE_DAYS = 60  # 12 weeks * 5 days
    
    def check_eligibility(self, employee: Employee) -> Dict:
        """Check employee FMLA eligibility."""
        criteria = {
            "employed_12_months": employee.years_of_service >= 1,
            "hours_worked_1250": employee.meets_fmla_hours,
            "employer_covered": True,  # Assumed
        }
        
        eligible = all(criteria.values())
        
        return {
            "eligible": eligible,
            "criteria": criteria,
            "leave_remaining": employee.fmla_remaining if eligible else 0,
        }
    
    def validate_leave_request(
        self,
        employee: Employee,
        reason: FMLAQualifyingReason,
        requested_days: int,
    ) -> Dict:
        """Validate FMLA leave request."""
        eligibility = self.check_eligibility(employee)
        
        if not eligibility["eligible"]:
            return {
                "approved": False,
                "reason": "Employee not FMLA eligible",
            }
        
        if requested_days > employee.fmla_remaining:
            return {
                "approved": False,
                "reason": f"Exceeds remaining leave ({employee.fmla_remaining} days)",
                "partial_approval_possible": True,
                "max_approved": employee.fmla_remaining,
            }
        
        return {
            "approved": True,
            "days_approved": requested_days,
            "reason": reason.name,
            "job_protection": True,
            "health_insurance_continues": True,
        }


class WageHourCompliance:
    """Checker for wage and hour compliance (FLSA)."""
    
    MINIMUM_WAGE = Fraction(725, 100)  # $7.25 federal
    OVERTIME_THRESHOLD = 40  # Hours per week
    OVERTIME_RATE = Fraction(15, 10)  # 1.5x regular rate
    
    def check_minimum_wage(self, hourly_rate: Fraction) -> Dict:
        """Check if wage meets minimum."""
        return {
            "compliant": hourly_rate >= self.MINIMUM_WAGE,
            "wage": hourly_rate,
            "minimum": self.MINIMUM_WAGE,
            "shortfall": max(self.MINIMUM_WAGE - hourly_rate, Fraction(0)),
        }
    
    def calculate_overtime_pay(
        self,
        regular_rate: Fraction,
        hours_worked: int,
    ) -> Dict:
        """Calculate overtime pay due."""
        if hours_worked <= self.OVERTIME_THRESHOLD:
            return {
                "regular_hours": hours_worked,
                "overtime_hours": 0,
                "regular_pay": regular_rate * hours_worked,
                "overtime_pay": Fraction(0),
                "total_pay": regular_rate * hours_worked,
            }
        
        regular_hours = self.OVERTIME_THRESHOLD
        overtime_hours = hours_worked - regular_hours
        
        regular_pay = regular_rate * regular_hours
        overtime_rate = regular_rate * self.OVERTIME_RATE
        overtime_pay = overtime_rate * overtime_hours
        
        return {
            "regular_hours": regular_hours,
            "overtime_hours": overtime_hours,
            "regular_pay": regular_pay,
            "overtime_pay": overtime_pay,
            "total_pay": regular_pay + overtime_pay,
        }
    
    def detect_wage_theft(
        self,
        hours_worked: int,
        hours_paid: int,
        regular_rate: Fraction,
    ) -> Dict:
        """Detect potential wage theft."""
        unpaid_hours = hours_worked - hours_paid
        
        # Calculate what should have been paid
        correct_calc = self.calculate_overtime_pay(regular_rate, hours_worked)
        actual_pay = regular_rate * hours_paid
        
        theft_amount = correct_calc["total_pay"] - actual_pay
        
        return {
            "wage_theft_detected": unpaid_hours > 0 or theft_amount > 0,
            "unpaid_hours": unpaid_hours,
            "theft_amount": max(theft_amount, Fraction(0)),
            "hours_worked": hours_worked,
            "hours_paid": hours_paid,
        }


class EmploymentComplianceChecker:
    """Comprehensive employment law compliance checker."""
    
    def __init__(self):
        self.title_vii_analyzer = TitleVIIAnalyzer()
        self.ada_analyzer = ADAAccommodationAnalyzer()
        self.fmla_checker = FMLAEligibilityChecker()
        self.wage_checker = WageHourCompliance()
    
    def check_employment_action(
        self,
        action: EmploymentAction,
        employee: Employee,
    ) -> Dict:
        """Check employment action for compliance."""
        issues = []
        
        # Check for discrimination
        if employee.protected_classes:
            # Would need claim to analyze
            pass
        
        # Check for retaliation
        if (action.days_since_protected_activity is not None and
            action.days_since_protected_activity <= 90):
            issues.append("Potential retaliation - action shortly after protected activity")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
        }


# Convenience functions
def check_title_vii_prohibits_discrimination(
    protected_class: str,
    adverse_action: str,
    comparator_treatment: str,
) -> Dict:
    """Quick check for Title VII violation indicators."""
    return {
        "protected_class": protected_class,
        "adverse_action": adverse_action,
        "potential_violation": adverse_action.lower() in ["termination", "demotion", "pay_cut"],
        "investigation_recommended": True,
    }


def check_ada_accommodation_required(
    has_disability: bool,
    accommodation_requested: str,
    cost_estimate: float,
) -> Dict:
    """Quick check for ADA accommodation requirements."""
    if not has_disability:
        return {"accommodation_required": False, "reason": "No qualifying disability"}
    
    undue_hardship = cost_estimate > 50000
    
    return {
        "accommodation_required": not undue_hardship,
        "undue_hardship": undue_hardship,
        "interactive_process_required": True,
    }


def check_fmla_eligibility(
    months_employed: int,
    hours_worked: int,
) -> Dict:
    """Quick check for FMLA eligibility."""
    eligible = months_employed >= 12 and hours_worked >= 1250
    
    return {
        "eligible": eligible,
        "months_criteria": months_employed >= 12,
        "hours_criteria": hours_worked >= 1250,
        "leave_entitlement": 60 if eligible else 0,  # 12 weeks in days
    }
