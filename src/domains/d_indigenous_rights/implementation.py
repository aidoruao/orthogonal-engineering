"""D_INDIGENOUS_RIGHTS implementation — Indigenous Rights Law

Implements indigenous rights including tribal sovereignty, ICWA placement
preferences, trust responsibility, treaty rights, and consultation requirements.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: ICWA (25 U.S.C. §1901), NHPA §106, Tribal Law and Order Act

Biblical: Leviticus 25:23 — "The land must not be sold permanently, because
the land is mine and you reside in my land as foreigners and strangers."
Also: Acts 10:34-35 — God shows no favoritism but accepts all nations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class TribalEntityType(Enum):
    """Types of tribal entities."""
    FEDERALLY_RECOGNIZED_TRIBE = auto()
    STATE_RECOGNIZED_TRIBE = auto()
    TRIBAL_ORGANIZATION = auto()
    NATIVE_CORPORATION = auto()  # ANCSA


class TreatyRightType(Enum):
    """Types of treaty rights."""
    HUNTING = auto()
    FISHING = auto()
    GATHERING = auto()
    WATER_RIGHTS = auto()
    LAND_USE = auto()
    SELF_GOVERNANCE = auto()
    TAX_IMMUNITY = auto()


class ICWAPreference(Enum):
    """ICWA placement preferences in order."""
    EXTENDED_FAMILY = auto()
    TRIBAL_MEMBER = auto()
    OTHER_INDIAN_FAMILY = auto()
    INSTITUTION_APPROVED_BY_TRIBE = auto()


class ConsultationType(Enum):
    """Types of required tribal consultation."""
    NHPA_SECTION_106 = auto()  # Historic preservation
    NEPA = auto()              # Environmental review
    SELF_DETERMINATION = auto()  # Self-Determination Act
    EXECUTIVE_ORDER_13175 = auto()  # Consultation and coordination


class TrustAssetType(Enum):
    """Types of trust assets managed by federal government."""
    LAND = auto()
    NATURAL_RESOURCES = auto()
    MINERALS = auto()
    WATER_RIGHTS = auto()
    PER_CAPITA_PAYMENTS = auto()


@dataclass
class TribalNation:
    """A federally recognized tribal nation."""
    tribe_id: str
    name: str
    alternate_names: List[str] = field(default_factory=list)
    
    # Federal recognition
    federally_recognized: bool = False
    recognition_date: Optional[datetime] = None
    federal_register_citation: Optional[str] = None
    
    # Governance
    has_constitution: bool = False
    ira_tribe: bool = False  # Indian Reorganization Act
    
    # Territory
    reservation_acres: Fraction = Fraction(0)
    trust_land_acres: Fraction = Fraction(0)
    ancestral_territory: List[str] = field(default_factory=list)
    
    # ICWA
    icwa_applies: bool = True
    tribal_court_established: bool = False


@dataclass
class IndianChild:
    """An Indian child under ICWA."""
    child_id: str
    name: str
    date_of_birth: datetime
    
    # Eligibility
    enrolled_tribe_id: Optional[str] = None
    eligible_for_enrollment: bool = False
    biological_parent_enrolled: bool = False
    
    # ICWA status
    icwa_eligible: bool = False  # Either enrolled or eligible
    
    # Placement
    current_placement_type: Optional[str] = None
    placement_preference_followed: Optional[bool] = None
    
    def __post_init__(self):
        """Determine ICWA eligibility."""
        self.icwa_eligible = bool(self.enrolled_tribe_id) or self.eligible_for_enrollment


@dataclass
class Placement:
    """A placement for an Indian child."""
    placement_id: str
    child_id: str
    placement_type: str  # "foster_family", "relative", "institution"
    
    # ICWA preference compliance
    is_extended_family: bool = False
    is_tribal_member: bool = False
    is_other_indian: bool = False
    is_tribally_approved_institution: bool = False
    
    # Good cause determination
    good_cause_exception: Optional[str] = None  # Reason if preference not followed


@dataclass
class Treaty:
    """A treaty between U.S. and tribal nation."""
    treaty_id: str
    treaty_name: str
    signing_date: datetime
    ratification_date: Optional[datetime] = None
    
    # Parties
    tribal_signatories: List[str] = field(default_factory=list)
    us_representative: Optional[str] = None
    
    # Rights reserved
    reserved_rights: List[TreatyRightType] = field(default_factory=list)
    ceded_territory: List[str] = field(default_factory=list)
    
    # Status
    supreme_court_cases: List[str] = field(default_factory=list)
    still_in_force: bool = True


@dataclass
class TrustAsset:
    """A trust asset held by the federal government for tribal benefit."""
    asset_id: str
    asset_type: TrustAssetType
    beneficiary_tribe_id: str
    
    # Management
    managing_agency: str  # "BIA", "BLM", etc.
    revenue_generated: Fraction = Fraction(0)
    management_fees: Fraction = Fraction(0)


@dataclass
class ConsultationRecord:
    """A record of tribal consultation."""
    consultation_id: str
    consultation_type: ConsultationType
    agency_id: str
    tribe_id: str
    
    # Timing
    initiated_date: datetime
    completed_date: Optional[datetime] = None
    
    # Outcome
    tribe_response: Optional[str] = None
    agency_considered_input: bool = False
    concerns_addressed: bool = False


class ICWAComplianceChecker:
    """Checker for ICWA (Indian Child Welfare Act) compliance."""
    
    def check_icwa_applicability(self, child: IndianChild) -> Dict:
        """Check if ICWA applies to child."""
        # ICWA applies if child is:
        # 1. Member of federally recognized tribe, OR
        # 2. Eligible for membership AND biological parent is member
        
        if child.enrolled_tribe_id:
            return {
                "icwa_applies": True,
                "basis": "enrolled_member",
                "tribe_id": child.enrolled_tribe_id,
            }
        
        if child.eligible_for_enrollment and child.biological_parent_enrolled:
            return {
                "icwa_applies": True,
                "basis": "eligible_and_parent_enrolled",
            }
        
        return {
            "icwa_applies": False,
            "basis": None,
        }
    
    def check_placement_preference_compliance(self, placement: Placement) -> Dict:
        """Check if placement follows ICWA preference order."""
        # ICWA preference order:
        # 1. Extended family member
        # 2. Tribal member
        # 3. Other Indian family
        # 4. Institution approved by tribe
        
        preference_order = [
            placement.is_extended_family,
            placement.is_tribal_member,
            placement.is_other_indian,
            placement.is_tribally_approved_institution,
        ]
        
        # Check if any preference was followed
        preference_followed = any(preference_order)
        
        if preference_followed:
            return {
                "preference_followed": True,
                "highest_preference_met": self._get_highest_preference(placement),
                "good_cause_required": False,
            }
        
        # If preference not followed, good cause required
        return {
            "preference_followed": False,
            "good_cause_required": True,
            "good_cause_documented": placement.good_cause_exception is not None,
        }
    
    def _get_highest_preference(self, placement: Placement) -> Optional[str]:
        """Get the highest ICWA preference met."""
        if placement.is_extended_family:
            return "extended_family"
        if placement.is_tribal_member:
            return "tribal_member"
        if placement.is_other_indian:
            return "other_indian"
        if placement.is_tribally_approved_institution:
            return "tribally_approved_institution"
        return None
    
    def check_active_efforts_requirement(self, removal_date: datetime) -> Dict:
        """Check active efforts requirement (higher than reasonable efforts)."""
        # ICWA requires "active efforts" to prevent breakup of Indian family
        # This is higher standard than ASFA's "reasonable efforts"
        
        return {
            "active_efforts_required": True,
            "standard": "active_efforts",  # Higher than reasonable efforts
            "efforts_must_include": [
                "Tribal cultural programs",
                "Extended family participation",
                "Tribal social services",
                "Tribal funding programs",
            ],
        }
    
    def check_qualified_expert_witness_requirement(self) -> Dict:
        """Check if qualified expert witness is required."""
        # ICWA requires qualified expert witness testimony for foster care placement
        # and termination of parental rights
        
        return {
            "qew_required": True,
            "qew_qualifications": [
                "Knowledge of tribal child-rearing practices",
                "Knowledge of Indian cultural standards",
                "Experience with Indian family organization",
            ],
        }


class TribalSovereigntyAnalyzer:
    """Analyzer for tribal sovereignty issues."""
    
    def analyze_criminal_jurisdiction(
        self,
        crime_location: str,  # "reservation", "trust_land", "fee_land", "off_reservation"
        victim_tribal_status: str,  # "tribal_member", "non_indian"
        defendant_tribal_status: str,
        crime_type: str,  # "misdemeanor", "felony", "major_crime"
    ) -> Dict:
        """Analyze criminal jurisdiction under tribal/state/federal law."""
        
        jurisdiction = {}
        
        # On reservation with tribal defendant
        if crime_location in ["reservation", "trust_land"]:
            if defendant_tribal_status == "tribal_member":
                # Tribal court has jurisdiction
                jurisdiction["tribal"] = True
                
                # Major crimes (18 USC 1153) also federal
                if crime_type == "major_crime":
                    jurisdiction["federal"] = True
            
            # Non-Indian defendant on reservation
            if defendant_tribal_status == "non_indian":
                # Oliphant v. Suquamish - tribal courts lack criminal jurisdiction
                if victim_tribal_status == "tribal_member":
                    # Federal jurisdiction under ICRA
                    jurisdiction["federal"] = True
                else:
                    # State jurisdiction (PL 280 or general)
                    jurisdiction["state"] = True
        
        return jurisdiction
    
    def check_tribal_tax_immunity(self, tribe: TribalNation, tax_type: str) -> Dict:
        """Check tribal sovereign immunity from taxation."""
        # Tribes generally immune from state taxation on reservation
        # Can be waived by Congress or tribe
        
        if tax_type in ["state_income", "state_property", "state_sales"]:
            if tribe.federally_recognized:
                return {
                    "immune": True,
                    "basis": "tribal_sovereign_immunity",
                    "can_be_waived": True,
                }
        
        return {
            "immune": False,
            "tax_applies": tax_type,
        }


class TrustResponsibilityChecker:
    """Checker for federal trust responsibility."""
    
    def check_trust_responsibility(self, tribe: TribalNation) -> Dict:
        """Check federal trust responsibility obligations."""
        obligations = []
        
        if tribe.federally_recognized:
            obligations.extend([
                "Protection of tribal sovereignty",
                "Management of trust assets",
                "Health services (IHS)",
                "Education services (BIE)",
                "Law enforcement support",
            ])
        
        return {
            "trust_responsibility_exists": tribe.federally_recognized,
            "obligations": obligations,
            "breach_potential": tribe.trust_land_acres == 0,  # Simplified
        }


class ConsultationComplianceChecker:
    """Checker for tribal consultation requirements."""
    
    def check_nhpa_section_106(
        self,
        undertaking_affects_historic_properties: bool,
        tribal_sacred_sites_affected: bool,
        consultation_conducted: bool,
    ) -> Dict:
        """Check NHPA Section 106 consultation compliance."""
        if undertaking_affects_historic_properties or tribal_sacred_sites_affected:
            consultation_required = True
        else:
            consultation_required = False
        
        if consultation_required and not consultation_conducted:
            return {
                "compliant": False,
                "violation": "NHPA Section 106 consultation not conducted",
                "remedy": "Halt undertaking, conduct consultation",
            }
        
        return {
            "compliant": True,
            "consultation_required": consultation_required,
            "consultation_conducted": consultation_conducted,
        }
    
    def check_executive_order_13175(self, policy_tribal_implications: bool) -> Dict:
        """Check Executive Order 13175 consultation compliance."""
        if policy_tribal_implications:
            return {
                "consultation_required": True,
                "timing": "early_and_meaningful",
                "documentation_required": True,
            }
        
        return {
            "consultation_required": False,
        }


class IndigenousRightsEnforcer:
    """Comprehensive enforcer for indigenous rights."""
    
    def __init__(self):
        self.icwa_checker = ICWAComplianceChecker()
        self.sovereignty_analyzer = TribalSovereigntyAnalyzer()
        self.trust_checker = TrustResponsibilityChecker()
        self.consultation_checker = ConsultationComplianceChecker()
    
    def conduct_icwa_compliance_review(self, child: IndianChild, placement: Placement) -> Dict:
        """Conduct ICWA compliance review."""
        icwa_applicability = self.icwa_checker.check_icwa_applicability(child)
        placement_compliance = self.icwa_checker.check_placement_preference_compliance(placement)
        
        return {
            "child_id": child.child_id,
            "icwa_applies": icwa_applicability["icwa_applies"],
            "placement_preference_followed": placement_compliance["preference_followed"],
            "good_cause_required": placement_compliance.get("good_cause_required", False),
        }


# Convenience functions
def check_icwa_applicability(enrolled: bool, eligible: bool, parent_enrolled: bool) -> Dict:
    """Quick check for ICWA applicability."""
    applies = enrolled or (eligible and parent_enrolled)
    return {
        "icwa_applies": applies,
        "basis": "enrolled" if enrolled else "eligible" if applies else None,
    }


def check_tribal_criminal_jurisdiction(defendant_indian: bool, location: str) -> Dict:
    """Quick check for tribal criminal jurisdiction."""
    if location in ["reservation", "trust_land"]:
        return {
            "tribal_jurisdiction": defendant_indian,
            "federal_jurisdiction": True,  # Major crimes
            "state_jurisdiction": not defendant_indian,  # Non-Indian on res
        }
    return {
        "tribal_jurisdiction": False,
        "federal_jurisdiction": False,
        "state_jurisdiction": True,
    }


def check_trust_land_status(land_status: str) -> Dict:
    """Quick check for trust land status."""
    is_trust = land_status == "trust"
    return {
        "trust_land": is_trust,
        "tax_exempt": is_trust,
        "federal_management": is_trust,
    }
