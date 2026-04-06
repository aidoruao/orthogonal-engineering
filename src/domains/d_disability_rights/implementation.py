"""D_DISABILITY_RIGHTS implementation — Disability Rights Law

Implements disability rights protections including ADA Titles I-III,
reasonable accommodation requirements, and accessibility standards.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: ADA (42 U.S.C. §12101), Section 504, WCAG 2.1, Rehabilitation Act

Biblical: Matthew 11:5 — "The blind receive sight, the lame walk, those who
have leprosy are cleansed, the deaf hear, the dead are raised, and the good
news is proclaimed to the poor."
Also: Leviticus 19:14 — "Do not curse the deaf or put a stumbling block in
front of the blind, but fear your God. I am the LORD."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class DisabilityType(Enum):
    """Categories of disability under ADA."""
    PHYSICAL = auto()
    SENSORY = auto()  # Vision, hearing
    COGNITIVE = auto()
    PSYCHIATRIC = auto()
    NEUROLOGICAL = auto()
    MOBILITY = auto()
    CHRONIC_HEALTH = auto()


class ADATitle(Enum):
    """Titles of the ADA."""
    TITLE_I_EMPLOYMENT = auto()
    TITLE_II_PUBLIC_SERVICES = auto()
    TITLE_III_PUBLIC_ACCOMMODATIONS = auto()
    TITLE_IV_TELECOMMUNICATIONS = auto()


class AccommodationType(Enum):
    """Types of reasonable accommodations."""
    JOB_RESTRUCTURING = auto()
    SCHEDULE_MODIFICATION = auto()
    EQUIPMENT_PROVISION = auto()
    POLICY_MODIFICATION = auto()
    ACCESSIBLE_FACILITY = auto()
    INTERPRETER_SERVICES = auto()
    MODIFIED_TRAINING = auto()


class EntityType(Enum):
    """Types of entities covered by ADA."""
    PRIVATE_EMPLOYER = auto()  # 15+ employees for Title I
    STATE_LOCAL_GOVERNMENT = auto()  # Title II
    PUBLIC_ACCOMMODATION = auto()  # Title III
    TRANSPORTATION = auto()
    TELECOMMUNICATIONS = auto()


@dataclass
class Individual:
    """An individual with a disability."""
    individual_id: str
    name: str
    disabilities: Set[DisabilityType]
    accommodation_needs: List[str] = field(default_factory=list)
    
    # Essential functions they can perform
    can_perform_essential_functions: Dict[str, bool] = field(default_factory=dict)
    
    # Interactive process participation
    engaged_in_interactive_process: bool = True


@dataclass
class Employer:
    """An employer covered by ADA Title I."""
    employer_id: str
    name: str
    employee_count: int
    entity_type: EntityType = EntityType.PRIVATE_EMPLOYER
    
    @property
    def ada_covered(self) -> bool:
        """ADA Title I covers employers with 15+ employees."""
        return self.employee_count >= 15


@dataclass
class AccommodationRequest:
    """A request for reasonable accommodation."""
    request_id: str
    individual_id: str
    employer_id: str
    accommodation_type: AccommodationType
    description: str
    request_date: datetime
    
    # Interactive process
    interactive_process_started: Optional[datetime] = None
    interactive_process_completed: Optional[datetime] = None
    
    # Outcome
    granted: Optional[bool] = None
    denial_reason: Optional[str] = None  # "undue_hardship", etc.


@dataclass
class AccessibilityBarrier:
    """A physical or digital accessibility barrier."""
    barrier_id: str
    location: str  # Building, website, etc.
    barrier_type: str  # "steps", "narrow_doorway", "no_captions", etc.
    wcag_guideline: Optional[str] = None  # WCAG 2.1 guideline number
    remediation_cost: Optional[Fraction] = None
    priority: str = "medium"  # "high", "medium", "low"


@dataclass
class PhysicalFacility:
    """A physical facility subject to ADA accessibility requirements."""
    facility_id: str
    name: str
    address: str
    entity_type: EntityType
    
    # Accessibility features
    has_accessible_entrance: bool = False
    has_accessible_restroom: bool = False
    has_accessible_parking: bool = False
    has_elevator: bool = False
    has_braille_signage: bool = False
    has_hearing_loop: bool = False
    
    barriers: List[AccessibilityBarrier] = field(default_factory=list)


@dataclass
class DigitalContent:
    """Digital content subject to accessibility requirements."""
    content_id: str
    content_type: str  # "website", "document", "video", "application"
    owner_id: str
    
    # WCAG 2.1 compliance
    has_alt_text: bool = False
    has_captions: bool = False
    has_keyboard_navigation: bool = False
    has_screen_reader_support: bool = False
    has_sufficient_contrast: bool = False
    
    wcag_level: str = "none"  # "A", "AA", "AAA", "none"


class ReasonableAccommodationAnalyzer:
    """Analyzer for reasonable accommodation requests under ADA."""
    
    # Undue hardship factors (EEOC guidance)
    UNDUE_HARDSHIP_FACTORS = [
        "nature_and_cost",
        "financial_resources",
        "number_of_employees",
        "impact_on_operations",
    ]
    
    def __init__(self):
        self.requests: Dict[str, AccommodationRequest] = {}
    
    def check_interactive_process(self, request: AccommodationRequest) -> Dict:
        """Check if interactive process was followed."""
        if not request.interactive_process_started:
            return {
                "compliant": False,
                "reason": "Interactive process not initiated",
                "violation": "ADA requires good faith interactive process",
            }
        
        # Interactive process should be completed before decision
        if request.granted is not None and not request.interactive_process_completed:
            return {
                "compliant": False,
                "reason": "Decision made before completing interactive process",
            }
        
        return {
            "compliant": True,
            "process_duration_days": (
                (request.interactive_process_completed - request.interactive_process_started).days
                if request.interactive_process_completed else None
            ),
        }
    
    def evaluate_accommodation(
        self,
        request: AccommodationRequest,
        employer: Employer,
        individual: Individual,
        estimated_cost: Fraction,
        employer_revenue: Fraction,
    ) -> Dict:
        """Evaluate whether accommodation is reasonable or undue hardship."""
        # Must be covered by ADA
        if not employer.ada_covered:
            return {
                "covered_by_ada": False,
                "accommodation_required": False,
                "reason": "Employer has fewer than 15 employees",
            }
        
        # Check if individual has disability under ADA
        if not individual.disabilities:
            return {
                "covered_by_ada": True,
                "qualified_individual": False,
                "accommodation_required": False,
                "reason": "No qualifying disability",
            }
        
        # Check undue hardship (cost > reasonable threshold)
        # Simplified: cost > 5% of annual revenue = undue hardship
        cost_ratio = estimated_cost / employer_revenue if employer_revenue > 0 else Fraction(0)
        undue_hardship = cost_ratio > Fraction(5, 100)
        
        if undue_hardship:
            return {
                "covered_by_ada": True,
                "qualified_individual": True,
                "accommodation_granted": False,
                "denial_reason": "undue_hardship",
                "cost_ratio": float(cost_ratio),
                "alternative_accommodation_required": True,
            }
        
        return {
            "covered_by_ada": True,
            "qualified_individual": True,
            "accommodation_granted": True,
            "effective_accommodation": True,
            "undue_hardship": False,
        }


class AccessibilityComplianceChecker:
    """Checker for ADA accessibility compliance."""
    
    WCAG_AA_REQUIREMENTS = {
        "alt_text": True,
        "keyboard_navigation": True,
        "captions": True,
        "sufficient_contrast": True,
        "resizable_text": True,
        "consistent_navigation": True,
    }
    
    def __init__(self):
        self.violations: List[Dict] = []
    
    def check_physical_accessibility(self, facility: PhysicalFacility) -> Dict:
        """Check physical facility ADA compliance."""
        issues = []
        
        # Title III public accommodations requirements
        if facility.entity_type == EntityType.PUBLIC_ACCOMMODATION:
            if not facility.has_accessible_entrance:
                issues.append("No accessible entrance")
            if not facility.has_accessible_restroom:
                issues.append("No accessible restroom")
            if not facility.has_accessible_parking:
                issues.append("No accessible parking")
        
        # New construction/alterations need elevator if multi-story
        # (simplified check)
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "barriers_identified": len(facility.barriers),
            "priority_remediations": [b for b in facility.barriers if b.priority == "high"],
        }
    
    def check_digital_accessibility(self, content: DigitalContent) -> Dict:
        """Check digital content WCAG 2.1 compliance."""
        wcag_aa_checks = {
            "alt_text": content.has_alt_text,
            "keyboard_navigation": content.has_keyboard_navigation,
            "captions": content.has_captions,
            "sufficient_contrast": content.has_sufficient_contrast,
        }
        
        passed = sum(wcag_aa_checks.values())
        total = len(wcag_aa_checks)
        
        # WCAG AA requires all these
        wcag_aa_compliant = all(wcag_aa_checks.values())
        
        return {
            "wcag_aa_compliant": wcag_aa_compliant,
            "checks_passed": passed,
            "checks_total": total,
            "missing": [k for k, v in wcag_aa_checks.items() if not v],
            "current_level": "AA" if wcag_aa_compliant else content.wcag_level,
        }
    
    def check_program_accessibility(self, services: List[str], barriers: List[str]) -> Dict:
        """Check if programs/services are accessible (Title II)."""
        # Title II requires program accessibility, not necessarily every facility
        # Can provide accessible alternative location
        
        if not barriers:
            return {
                "program_accessible": True,
                "method": "direct_access",
            }
        
        # With barriers, must provide alternative
        return {
            "program_accessible": False,  # Until alternative provided
            "barriers": barriers,
            "required_action": "provide_accessible_alternative",
        }


class DisabilityRightsEnforcer:
    """Enforcer for disability rights compliance across domains."""
    
    def __init__(self):
        self.accommodation_analyzer = ReasonableAccommodationAnalyzer()
        self.accessibility_checker = AccessibilityComplianceChecker()
    
    def conduct_title_i_audit(self, employer: Employer) -> Dict:
        """Conduct ADA Title I (employment) compliance audit."""
        if not employer.ada_covered:
            return {
                "covered": False,
                "reason": f"Employer has {employer.employee_count} employees (need 15+)",
            }
        
        return {
            "covered": True,
            "requirements": [
                "Provide reasonable accommodations",
                "Engage in interactive process",
                "No disability discrimination in hiring",
                "Essential functions analysis",
            ],
        }
    
    def conduct_title_iii_audit(self, facility: PhysicalFacility) -> Dict:
        """Conduct ADA Title III (public accommodations) compliance audit."""
        physical = self.accessibility_checker.check_physical_accessibility(facility)
        
        return {
            "covered": facility.entity_type == EntityType.PUBLIC_ACCOMMODATION,
            "physical_compliance": physical["compliant"],
            "violations": physical["issues"],
            "remediation_priority": physical["priority_remediations"],
        }


# Convenience functions
def check_reasonable_accommodation_requirement(employer_employees: int) -> Dict:
    """Quick check if employer must provide reasonable accommodations."""
    return {
        "covered_by_ada": employer_employees >= 15,
        "threshold": 15,
        "actual": employer_employees,
    }


def check_wcag_compliance(has_alt_text: bool, has_captions: bool, has_keyboard: bool) -> Dict:
    """Quick WCAG AA compliance check."""
    checks = {
        "alt_text": has_alt_text,
        "captions": has_captions,
        "keyboard_navigation": has_keyboard,
    }
    return {
        "wcag_aa_compliant": all(checks.values()),
        "passed": sum(checks.values()),
        "total": len(checks),
    }


def check_undue_hardship_threshold(accommodation_cost: float, employer_revenue: float) -> Dict:
    """Check if accommodation cost exceeds undue hardship threshold."""
    if employer_revenue == 0:
        return {"undue_hardship": True, "reason": "No revenue data"}
    
    ratio = accommodation_cost / employer_revenue
    threshold = 0.05  # 5%
    
    return {
        "undue_hardship": ratio > threshold,
        "cost_ratio": ratio,
        "threshold": threshold,
    }
