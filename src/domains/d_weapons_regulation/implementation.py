"""D_WEAPONS_REGULATION implementation — Weapons Regulation Law

Implements firearms regulations including GCA background checks, NFA items,
prohibited persons, and state preemption analysis.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: GCA (18 U.S.C. §922), NFA (26 U.S.C. §5801), Brady Act, FOPA

Biblical: Matthew 26:52 — "Put your sword back in its place... for all who
draw the sword will die by the sword."
Also: Ecclesiastes 3:8 — "a time for war and a time for peace."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class FirearmType(Enum):
    """Types of firearms."""
    HANDGUN = auto()
    RIFLE = auto()
    SHOTGUN = auto()
    RECEIVER = auto()
    FRAME = auto()
    SILENCER = auto()  # NFA item
    MACHINE_GUN = auto()  # NFA item
    SHORT_BARRELED_RIFLE = auto()  # NFA item (SBR)
    SHORT_BARRELED_SHOTGUN = auto()  # NFA item (SBS)
    DESTRUCTIVE_DEVICE = auto()  # NFA item
    ANY_OTHER_WEAPON = auto()  # NFA item (AOW)


class FirearmCategory(Enum):
    """Regulatory categories."""
    TITLE_I = auto()  # Standard GCA firearms
    TITLE_II_NFA = auto()  # NFA-regulated items
    ANTIQUE = auto()  # Pre-1899, exempt


class DisqualifierType(Enum):
    """Types of prohibiting factors under GCA."""
    FELONY_CONVICTION = auto()
    DOMESTIC_VIOLENCE_MISDEMEANOR = auto()
    DOMESTIC_VIOLENCE_RESTRAINING_ORDER = auto()
    FUGITIVE_FROM_JUSTICE = auto()
    UNLAWFUL_DRUG_USER = auto()
    ADJUDICATED_MENTAL_DEFECTIVE = auto()
    DISHONORABLE_DISCHARGE = auto()
    RENOUNCED_CITIZENSHIP = auto()
    ILLEGAL_ALIEN = auto()
    UNDER_INDICTMENT = auto()


class TransferType(Enum):
    """Types of firearm transfers."""
    FFL_SALE = auto()  # Dealer sale
    PRIVATE_SALE = auto()  # Private party
    GIFT = auto()
    INHERITANCE = auto()
    ESTATE = auto()


class NICSResult(Enum):
    """NICS background check results."""
    PROCEED = auto()
    DELAY = auto()
    DENY = auto()


@dataclass
class Firearm:
    """A firearm or firearm component."""
    firearm_id: str
    serial_number: Optional[str]  # None for pre-GCA or homemade
    manufacturer: str
    model: str
    
    firearm_type: FirearmType
    category: FirearmCategory
    
    # NFA items
    nfa_registered: bool = False
    nfa_tax_stamp_number: Optional[str] = None
    barrel_length_inches: Optional[float] = None
    overall_length_inches: Optional[float] = None
    
    @property
    def requires_nfa_registration(self) -> bool:
        """Check if firearm requires NFA registration."""
        return self.category == FirearmCategory.TITLE_II_NFA


@dataclass
class Person:
    """A person who may purchase or possess firearms."""
    person_id: str
    name: str
    date_of_birth: datetime
    citizenship: str
    
    # Residency
    state_of_residence: str
    
    # Prohibiting factors
    disqualifiers: Set[DisqualifierType] = field(default_factory=set)
    felony_convictions: List[Dict] = field(default_factory=list)
    dv_convictions: List[Dict] = field(default_factory=list)
    active_restraining_orders: List[Dict] = field(default_factory=list)
    
    # NICS
    nics_appeal_pending: bool = False


@dataclass
class FFLDealer:
    """Federal Firearms License holder."""
    ffl_number: str
    business_name: str
    license_type: str  # "01"=dealer, "02"=pawnbroker, "07"=manufacturer
    
    # Compliance
    bound_book_current: bool = True
    last_atf_inspection: Optional[datetime] = None
    violations: List[str] = field(default_factory=list)


@dataclass
class NICSCheck:
    """A NICS background check."""
    nics_transaction_number: str
    transferee_id: str
    submit_date: datetime
    
    result: Optional[NICSResult] = None
    result_date: Optional[datetime] = None
    appeal_number: Optional[str] = None
    
    # Brady Act: FFL may transfer after 3 business days if no response
    brady_transfer_date: Optional[datetime] = None


@dataclass
class FirearmTransfer:
    """A transfer of a firearm."""
    transfer_id: str
    firearm_id: str
    transferor_id: str
    transferee_id: str
    transfer_date: datetime
    transfer_type: TransferType
    
    ffl_involved: bool = False
    ffl_number: Optional[str] = None
    nics_ntn: Optional[str] = None
    nics_result: Optional[NICSResult] = None
    
    # For private sales in some states
    background_check_conducted: bool = False


class NICSBackgroundCheckSystem:
    """NICS (National Instant Criminal Background Check System)."""
    
    # Brady Act timing
    BRADY_TRANSFER_DAYS = 3
    
    def __init__(self):
        self.checks: Dict[str, NICSCheck] = {}
        self.denial_appeals: List[Dict] = []
    
    def check_prohibited_status(self, person: Person) -> Dict:
        """Check if person is prohibited from possessing firearms."""
        prohibitors = []
        
        # GCA Section 922(g) prohibitors
        if DisqualifierType.FELONY_CONVICTION in person.disqualifiers:
            prohibitors.append("Felony conviction")
        
        if DisqualifierType.DOMESTIC_VIOLENCE_MISDEMEANOR in person.disqualifiers:
            prohibitors.append("Domestic violence misdemeanor")
        
        if DisqualifierType.DOMESTIC_VIOLENCE_RESTRAINING_ORDER in person.disqualifiers:
            prohibitors.append("Active domestic violence restraining order")
        
        if DisqualifierType.FUGITIVE_FROM_JUSTICE in person.disqualifiers:
            prohibitors.append("Fugitive from justice")
        
        if DisqualifierType.UNLAWFUL_DRUG_USER in person.disqualifiers:
            prohibitors.append("Unlawful drug user")
        
        if DisqualifierType.ADJUDICATED_MENTAL_DEFECTIVE in person.disqualifiers:
            prohibitors.append("Adjudicated mental defective")
        
        if DisqualifierType.DISHONORABLE_DISCHARGE in person.disqualifiers:
            prohibitors.append("Dishonorable discharge")
        
        if DisqualifierType.RENOUNCED_CITIZENSHIP in person.disqualifiers:
            prohibitors.append("Renounced citizenship")
        
        if DisqualifierType.ILLEGAL_ALIEN in person.disqualifiers:
            prohibitors.append("Illegal/unlawful alien")
        
        prohibited = len(prohibitors) > 0
        
        return {
            "prohibited": prohibited,
            "prohibitors": prohibitors,
            "nics_result": NICSResult.DENY if prohibited else NICSResult.PROCEED,
        }
    
    def check_brady_transfer_eligibility(self, nics_check: NICSCheck) -> Dict:
        """Check if Brady transfer is permitted (no response after 3 days)."""
        if nics_check.result:
            # Already have a result
            return {
                "brady_transfer_permitted": nics_check.result == NICSResult.PROCEED,
                "reason": f"NICS result: {nics_check.result.name}",
            }
        
        # Calculate business days elapsed
        days_elapsed = (datetime.now() - nics_check.submit_date).days
        brady_eligible = days_eligible >= self.BRADY_TRANSFER_DAYS
        
        return {
            "brady_transfer_permitted": brady_eligible,
            "days_elapsed": days_elapsed,
            "brady_threshold_days": self.BRADY_TRANSFER_DAYS,
            "ffl_discretion": brady_eligible,  # FFL may transfer but not required
        }


class NFAComplianceChecker:
    """Checker for NFA (National Firearms Act) compliance."""
    
    # NFA tax amounts
    NFA_TAX_STANDARD = Fraction(200)
    NFA_TAX_AOW = Fraction(5)  # Any Other Weapon has lower tax
    
    def __init__(self):
        self.registrations: Dict[str, Dict] = {}
    
    def check_nfa_registration(self, firearm: Firearm) -> Dict:
        """Check if NFA item is properly registered."""
        if firearm.category != FirearmCategory.TITLE_II_NFA:
            return {
                "nfa_item": False,
                "registration_required": False,
            }
        
        if not firearm.nfa_registered:
            return {
                "nfa_item": True,
                "registration_required": True,
                "registered": False,
                "violation": "Unregistered NFA item - felony",
            }
        
        return {
            "nfa_item": True,
            "registration_required": True,
            "registered": True,
            "tax_stamp": firearm.nfa_tax_stamp_number,
        }
    
    def calculate_nfa_tax(self, firearm_type: FirearmType) -> Fraction:
        """Calculate NFA tax for transfer/registration."""
        if firearm_type == FirearmType.ANY_OTHER_WEAPON:
            return self.NFA_TAX_AOW
        return self.NFA_TAX_STANDARD
    
    def check_nfa_transfer_requirements(self, transfer: FirearmTransfer) -> Dict:
        """Check requirements for NFA transfer."""
        # NFA transfers require:
        # 1. ATF Form 4
        # 2. Tax stamp payment
        # 3. Chief Law Enforcement Officer notification
        # 4. Background check
        # 5. ATF approval (6-12 months)
        
        return {
            "form_4_required": True,
            "tax_payment_required": True,
            "cleo_notification_required": True,
            "atf_approval_required": True,
            "estimated_wait_days": "180-365",
            "trust_transfer": False,  # Could check if trust is involved
        }


class StatePreemptionAnalyzer:
    """Analyzer for state firearms law preemption."""
    
    def check_state_preemption(self, state: str, local_ordinance: Dict) -> Dict:
        """Check if local ordinance is preempted by state law."""
        # States with strong preemption
        strong_preemption_states = ["Arizona", "Florida", "Texas", "Pennsylvania"]
        
        # States allowing local regulation
        home_rule_states = ["California", "New York", "Illinois"]
        
        if state in strong_preemption_states:
            preempted = local_ordinance.get("type") in ["registration", "permitting", "ban"]
        elif state in home_rule_states:
            preempted = False
        else:
            # Mixed - check specific ordinance type
            preempted = local_ordinance.get("type") == "confiscation"
        
        return {
            "preempted": preempted,
            "state": state,
            "ordinance_type": local_ordinance.get("type"),
            "enforcement_permitted": not preempted,
        }


class FirearmsComplianceEnforcer:
    """Comprehensive enforcer for firearms regulations."""
    
    def __init__(self):
        self.nics_system = NICSBackgroundCheckSystem()
        self.nfa_checker = NFAComplianceChecker()
        self.preemption_analyzer = StatePreemptionAnalyzer()
    
    def conduct_ffl_audit(self, dealer: FFLDealer) -> Dict:
        """Conduct FFL compliance audit."""
        issues = []
        
        if not dealer.bound_book_current:
            issues.append("Bound book not current")
        
        if not dealer.last_atf_inspection:
            issues.append("No recent ATF inspection")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "violation_count": len(dealer.violations),
        }
    
    def analyze_transfer_compliance(self, transfer: FirearmTransfer) -> Dict:
        """Analyze compliance of a firearm transfer."""
        issues = []
        
        # Dealer sales require background check
        if transfer.transfer_type == TransferType.FFL_SALE and not transfer.nics_ntn:
            issues.append("FFL sale without NICS check")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "nics_check_documented": transfer.nics_ntn is not None,
        }


# Convenience functions
def check_prohibited_person(felony_conviction: bool, dv_misdemeanor: bool) -> Dict:
    """Quick check if person is prohibited from possessing firearms."""
    prohibited = felony_conviction or dv_misdemeanor
    reasons = []
    if felony_conviction:
        reasons.append("Felony conviction")
    if dv_misdemeanor:
        reasons.append("Domestic violence misdemeanor")
    
    return {
        "prohibited": prohibited,
        "reasons": reasons,
        "gca_section_922g": prohibited,
    }


def check_nfa_item(barrel_length: Optional[float], overall_length: Optional[float]) -> Dict:
    """Quick check if firearm configuration creates NFA item."""
    # SBR: Rifle < 16" barrel or < 26" overall
    # SBS: Shotgun < 18" barrel or < 26" overall
    
    is_nfa = False
    nfa_type = None
    
    if barrel_length is not None:
        if barrel_length < 16:
            is_nfa = True
            nfa_type = "SBR_or_SBS"
    
    if overall_length is not None:
        if overall_length < 26:
            is_nfa = True
            nfa_type = "SBR_or_SBS"
    
    return {
        "nfa_item": is_nfa,
        "type": nfa_type,
        "registration_required": is_nfa,
        "tax": 200 if is_nfa else 0,
    }


def check_private_sale_requirements(state: str) -> Dict:
    """Check background check requirements for private sales by state."""
    universal_background_check_states = [
        "California", "Colorado", "Connecticut", "Delaware",
        "Nevada", "New Jersey", "New Mexico", "New York",
        "Oregon", "Pennsylvania"  # Handguns only, "Rhode Island", "Vermont", "Washington"
    ]
    
    required = state in universal_background_check_states
    
    return {
        "background_check_required": required,
        "permitted_without_check": not required,
        "state": state,
    }
