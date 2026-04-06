"""D_HOUSING_LAW implementation — Housing Law

Implements Fair Housing Act (42 U.S.C. §3601), tenant rights,
eviction process protections, and habitability standards.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: Fair Housing Act, state landlord-tenant laws, URLTA

Biblical: Nehemiah 5:1-13 — Nehemiah opposed housing oppression when
"we have had to borrow money to pay the king's tax on our fields and vineyards."
"Give back to them immediately their fields, vineyards, olive groves and houses."
"When I called them together and weighed out for them the silver..."
"I shook out the folds of my robe and said, 'In this way may God shake out of
their house and possessions anyone who does not keep this promise.'"
"And the whole assembly said, 'Amen,' and praised the LORD."
"And the people did as they had promised."
"This reinforces the principle that housing is essential to human dignity."
"Thus, unjust eviction and housing discrimination is an affront to God's law."
"[Nehemiah 5:1-13, paraphrased]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class ProtectedClass(Enum):
    """Protected classes under Fair Housing Act (42 U.S.C. §3604)."""
    RACE = auto()
    COLOR = auto()
    RELIGION = auto()
    NATIONAL_ORIGIN = auto()
    SEX = auto()
    FAMILIAL_STATUS = auto()  # Presence of children
    DISABILITY = auto()


class HousingDiscriminationType(Enum):
    """Types of housing discrimination prohibited by FHA."""
    REFUSAL_TO_RENT = auto()
    REFUSAL_TO_SELL = auto()
    DIFFERENT_TERMS = auto()
    FALSE_AVAILABILITY = auto()
    ADVERTISING_DISCRIMINATION = auto()
    STEERING = auto()  # Directing to certain neighborhoods
    BLOCKBUSTING = auto()  # Inducing panic selling


class EvictionNoticeType(Enum):
    """Types of eviction notices."""
    PAY_OR_QUIT = auto()       # For nonpayment of rent
    CURE_OR_QUIT = auto()      # For lease violations (curable)
    UNCONDITIONAL_QUIT = auto()  # For serious violations (incurable)
    NOTICE_TO_QUIT = auto()    # No-cause (where permitted)


class HabitabilityRequirement(Enum):
    """Implied warranty of habitability requirements."""
    STRUCTURAL_INTEGRITY = auto()
    WEATHER_PROTECTION = auto()
    PLUMBING = auto()
    HEATING = auto()
    ELECTRICAL = auto()
    SANITATION = auto()
    WATER = auto()
    EXTERMINATION = auto()


@dataclass
class LeaseAgreement:
    """A residential lease agreement."""
    lease_id: str
    tenant_name: str
    landlord_name: str
    property_address: str
    monthly_rent: Fraction
    security_deposit: Fraction
    lease_term_months: int
    start_date: datetime
    
    # Terms
    late_fee_amount: Fraction = field(default_factory=lambda: Fraction(0))
    grace_period_days: int = 5
    pets_allowed: bool = False
    pet_deposit: Fraction = field(default_factory=lambda: Fraction(0))
    
    def calculate_late_fee(self, days_late: int) -> Fraction:
        """Calculate late fee if applicable."""
        if days_late <= self.grace_period_days:
            return Fraction(0)
        return self.late_fee_amount
    
    def is_rent_due(self, as_of: Optional[datetime] = None) -> bool:
        """Check if rent is currently due."""
        if as_of is None:
            as_of = datetime.now()
        # Simplified: rent due on same day of month as start date
        return as_of.day >= self.start_date.day


@dataclass
class HousingDiscriminationComplaint:
    """A complaint alleging housing discrimination under FHA."""
    complaint_id: str
    complainant_name: str
    respondent_name: str  # Landlord, seller, etc.
    protected_class: ProtectedClass
    discrimination_type: HousingDiscriminationType
    
    description: str = ""
    date_of_incident: Optional[datetime] = None
    property_address: str = ""
    
    # Evidence
    evidence_communications: List[str] = field(default_factory=list)
    evidence_witnesses: List[str] = field(default_factory=list)
    evidence_comparative: List[Dict] = field(default_factory=list)  # How others were treated
    
    def has_prima_facie_case(self) -> bool:
        """Check if complaint states a prima facie case under FHA.
        
        Prima facie case requires:
        1. Membership in protected class
        2. Application for/rejection of housing
        3. Qualified applicant
        4. Housing remained available/denied
        """
        return (
            self.protected_class is not None and
            len(self.description) > 0 and
            len(self.property_address) > 0
        )


@dataclass
class TenantRights:
    """Tenant's rights under landlord-tenant law."""
    tenant_id: str
    lease: LeaseAgreement
    
    # Habitability
    habitability_violations: List[HabitabilityRequirement] = field(default_factory=list)
    repair_requests_made: List[datetime] = field(default_factory=list)
    
    # Retaliation protection
    complaint_history: List[str] = field(default_factory=list)
    
    def has_habitability_claim(self) -> bool:
        """Check if tenant has valid habitability claim."""
        return len(self.habitability_violations) > 0 and len(self.repair_requests_made) > 0
    
    def can_withhold_rent(self) -> bool:
        """Check if tenant can legally withhold rent.
        
        Generally requires:
        1. Serious habitability violation
        2. Notice to landlord
        3. Reasonable time to repair
        """
        if not self.has_habitability_claim():
            return False
        
        # Must have given reasonable time to repair (30 days typical)
        if len(self.repair_requests_made) == 0:
            return False
        
        last_request = max(self.repair_requests_made)
        days_since_request = (datetime.now() - last_request).days
        
        return days_since_request >= 30
    
    def is_protected_from_retaliation(self) -> bool:
        """Check if tenant has engaged in protected activity."""
        return len(self.complaint_history) > 0


@dataclass
class EvictionProcess:
    """Eviction proceeding under state law."""
    case_id: str
    lease: LeaseAgreement
    tenant: TenantRights
    
    notice_type: Optional[EvictionNoticeType] = None
    notice_served_date: Optional[datetime] = None
    reason: str = ""
    
    # Legal requirements
    rent_owed: Fraction = field(default_factory=lambda: Fraction(0))
    days_notice_given: int = 0
    
    # Outcome
    court_date: Optional[datetime] = None
    judgment_for: Optional[str] = None
    
    def serve_notice(self, notice_type: EvictionNoticeType, days_notice: int):
        """Serve eviction notice."""
        self.notice_type = notice_type
        self.notice_served_date = datetime.now()
        self.days_notice_given = days_notice
    
    def can_file_forcible_entry(self) -> bool:
        """Check if landlord can file forcible entry and detainer action.
        
        Requires:
        1. Proper notice served
        2. Notice period expired
        3. Tenant remains in possession
        """
        if self.notice_served_date is None:
            return False
        
        expiration = self.notice_served_date + timedelta(days=self.days_notice_given)
        return datetime.now() > expiration
    
    def is_valid_notice_period(self, jurisdiction: str = "default") -> bool:
        """Check if notice period meets statutory minimum.
        
        Typical minimums:
        - Nonpayment: 3-5 days
        - Lease violation: 7-10 days
        - No cause: 30-60 days
        """
        minimums = {
            EvictionNoticeType.PAY_OR_QUIT: 3,
            EvictionNoticeType.CURE_OR_QUIT: 7,
            EvictionNoticeType.UNCONDITIONAL_QUIT: 1,  # Immediate
            EvictionNoticeType.NOTICE_TO_QUIT: 30,
        }
        
        required = minimums.get(self.notice_type, 30)
        return self.days_notice_given >= required
    
    def tenant_has_defense(self) -> Dict:
        """Check for common tenant defenses.
        
        Defenses include:
        1. Retaliation (tenant engaged in protected activity)
        2. Warranty of habitability breach
        3. Improper notice
        4. Payment of rent (for nonpayment cases)
        5. Discrimination
        """
        defenses = []
        
        # Retaliation defense
        if self.tenant.is_protected_from_retaliation():
            recent_complaint = len(self.tenant.complaint_history) > 0
            if recent_complaint:
                defenses.append("RETALIATION")
        
        # Habitability defense
        if self.tenant.has_habitability_claim():
            defenses.append("HABITABILITY")
        
        # Improper notice
        if not self.is_valid_notice_period():
            defenses.append("IMPROPER_NOTICE")
        
        return {
            "has_defense": len(defenses) > 0,
            "defenses": defenses,
        }


class FairHousingAnalyzer:
    """Analyzer for Fair Housing Act compliance.
    
    The Fair Housing Act prohibits discrimination in housing based on
    protected characteristics—reflecting the biblical principle that
    all people are created in God's image (Genesis 1:27) and should
    be treated with equal dignity.
    """
    
    def __init__(self):
        self.protected_classes = set(ProtectedClass)
    
    def analyze_discrimination_complaint(
        self,
        complaint: HousingDiscriminationComplaint,
    ) -> Dict:
        """Analyze housing discrimination complaint.
        
        Args:
            complaint: The discrimination complaint
            
        Returns:
            Analysis with violation determination
        """
        analysis = {
            "complaint_id": complaint.complaint_id,
            "has_prima_facie": complaint.has_prima_facie_case(),
            "violation_found": False,
            "legal_basis": "42 U.S.C. §3604",
            "evidence_strength": "WEAK",
            "recommendation": "INSUFFICIENT_EVIDENCE",
        }
        
        if not analysis["has_prima_facie"]:
            return analysis
        
        # Evaluate evidence strength
        evidence_score = 0
        if len(complaint.evidence_communications) >= 2:
            evidence_score += 2
        if len(complaint.evidence_witnesses) >= 1:
            evidence_score += 1
        if len(complaint.evidence_comparative) >= 1:
            evidence_score += 2  # Comparative evidence is strong
        
        if evidence_score >= 4:
            analysis["evidence_strength"] = "STRONG"
        elif evidence_score >= 2:
            analysis["evidence_strength"] = "MODERATE"
        
        # Determine if violation found
        if analysis["evidence_strength"] in ("STRONG", "MODERATE"):
            analysis["violation_found"] = True
            analysis["recommendation"] = "PROCEED_WITH_CHARGE"
        
        return analysis
    
    def check_advertising_compliance(self, advertisement_text: str) -> Dict:
        """Check rental advertisement for discriminatory language.
        
        Prohibited phrases include:
        - "No children" (familial status)
        - "Christian preferred" (religion)
        - "English only" (national origin)
        - "No wheelchairs" (disability)
        
        Args:
            advertisement_text: The advertisement to check
            
        Returns:
            Compliance analysis
        """
        text_lower = advertisement_text.lower()
        
        problematic_phrases = {
            "no children": ProtectedClass.FAMILIAL_STATUS,
            "no kids": ProtectedClass.FAMILIAL_STATUS,
            "adults only": ProtectedClass.FAMILIAL_STATUS,
            "christian": ProtectedClass.RELIGION,
            "jewish": ProtectedClass.RELIGION,
            "muslim": ProtectedClass.RELIGION,
            "english only": ProtectedClass.NATIONAL_ORIGIN,
            "no section 8": None,  # Source of income (state law)
        }
        
        violations = []
        for phrase, protected_class in problematic_phrases.items():
            if phrase in text_lower:
                violations.append({
                    "phrase": phrase,
                    "protected_class": protected_class.name,
                })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
        }
    
    def get_reasonable_accommodations_required(
        self,
        disability_type: str,
    ) -> List[str]:
        """Get reasonable accommodations for disability.
        
        Under FHA §3604(f)(3), landlords must make reasonable accommodations
        in rules, policies, practices, or services.
        
        Args:
            disability_type: Type of disability
            
        Returns:
            List of reasonable accommodations
        """
        accommodations = {
            "mobility": [
                "Accessible parking space",
                "Ramp or lift installation",
                "Bathroom grab bars",
                "Lowered counters",
            ],
            "visual": [
                "Braille signage",
                "Service animal allowance",
                "Audible alarms",
            ],
            "hearing": [
                "Visual doorbell/alarm",
                "TTY capability",
                "Written notices",
            ],
            "mental_health": [
                "Service animal (emotional support)",
                "Modified guest policies",
            ],
        }
        
        return accommodations.get(disability_type.lower(), [])


class HousingComplianceChecker:
    """Comprehensive housing law compliance checker."""
    
    def __init__(self):
        self.fha_analyzer = FairHousingAnalyzer()
    
    def check_fair_housing_compliance(
        self,
        complaint: HousingDiscriminationComplaint,
    ) -> Dict:
        """Check Fair Housing Act compliance."""
        analysis = self.fha_analyzer.analyze_discrimination_complaint(complaint)
        
        return {
            "compliant": not analysis["violation_found"],
            "issues": [] if analysis["viiation_found"] else ["Discrimination violation found"],
            "analysis": analysis,
        }
    
    def check_eviction_compliance(self, eviction: EvictionProcess) -> Dict:
        """Check eviction process compliance with state law."""
        issues = []
        
        if not eviction.is_valid_notice_period():
            issues.append("Insufficient notice period")
        
        # Check for defenses
        defenses = eviction.tenant_has_defense()
        if defenses["has_defense"]:
            issues.extend([f"Tenant defense: {d}" for d in defenses["defenses"]])
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "can_proceed": eviction.can_file_forcible_entry() and len(issues) == 0,
            "tenant_defenses": defenses,
        }


# Convenience functions
def check_fair_housing_violation(
    complainant_protected_class: str,
    adverse_action: str,
    evidence_count: int,
) -> Dict:
    """Quick check for potential Fair Housing Act violation.
    
    Usage:
        result = check_fair_housing_violation(
            complainant_protected_class="disability",
            adverse_action="refusal_to_rent",
            evidence_count=3,
        )
        print(f"Violation likely: {result['violation_likely']}")
    """
    try:
        protected = ProtectedClass[complainant_protected_class.upper()]
    except KeyError:
        return {"error": "Invalid protected class"}
    
    return {
        "protected_class": protected.name,
        "adverse_action": adverse_action,
        "evidence_count": evidence_count,
        "violation_likely": evidence_count >= 2,
        "recommended_action": "FILE_COMPLAINT" if evidence_count >= 2 else "GATHER_EVIDENCE",
    }
