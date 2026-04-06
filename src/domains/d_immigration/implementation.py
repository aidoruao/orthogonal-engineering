"""D_IMMIGRATION implementation — Immigration Law

Implements immigration law principles including visa categories,
asylum analysis, and INA (Immigration and Nationality Act) compliance.
Links to due process protections in constitutional layer.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: Immigration and Nationality Act (INA) 8 U.S.C. §1101 et seq.,
        8 CFR (Code of Federal Regulations)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from fractions import Fraction
from datetime import date, timedelta


class VisaCategory(Enum):
    """Major visa categories under INA."""
    # Family-sponsored (immigrant)
    F1_FAMILY = auto()  # Unmarried sons/daughters of US citizens
    F2A = auto()  # Spouses/children of LPRs
    F2B = auto()  # Unmarried sons/daughters of LPRs
    F3_FAMILY = auto()  # Married sons/daughters of US citizens
    F4_FAMILY = auto()  # Siblings of US citizens
    
    # Employment-based (immigrant)
    EB1 = auto()  # Priority workers (extraordinary ability)
    EB2 = auto()  # Advanced degree/professionals
    EB3 = auto()  # Skilled workers/professionals
    EB4 = auto()  # Special immigrants
    EB5 = auto()  # Immigrant investors
    
    # Nonimmigrant
    B1 = auto()   # Business visitor
    B2 = auto()   # Tourist visitor
    F1_STUDENT = auto()   # Student
    H1B = auto()  # Specialty occupation worker
    L1 = auto()   # Intracompany transferee
    O1 = auto()   # Extraordinary ability
    
    # Humanitarian
    ASYLUM = auto()      # Asylum seeker
    REFUGEE = auto()     # Refugee
    TPS = auto()         # Temporary Protected Status
    U_VISA = auto()      # Crime victims
    T_VISA = auto()      # Trafficking victims


class AdmissionClass(Enum):
    """Classes of admission under INA."""
    IMMIGRANT = auto()      # Lawful Permanent Resident (LPR)
    NONIMMIGRANT = auto()   # Temporary admission
    PAROLEE = auto()        # Humanitarian parole
    REFUGEE = auto()        # Refugee admission
    ASYLEE = auto()         # Asylum grantee


class RemovalGround(Enum):
    """Grounds of inadmissibility and deportability under INA."""
    HEALTH_GROUNDS = auto()           # INA §212(a)(1)
    CRIMINAL_GROUNDS = auto()         # INA §212(a)(2), §237(a)(2)
    SECURITY_GROUNDS = auto()         # INA §212(a)(3)
    PUBLIC_CHARGE = auto()            # INA §212(a)(4)
    LABOR_CERTIFICATION = auto()      # INA §212(a)(5)
    ILLEGAL_ENTRANTS = auto()         # INA §212(a)(6)
    DOCUMENTATION = auto()            # INA §212(a)(7)
    INELIGIBLE_FOR_CITIZENSHIP = auto()  # INA §212(a)(8)
    PREVIOUSLY_REMOVED = auto()       # INA §212(a)(9)
    MISCELLANEOUS = auto()            # INA §212(a)(10)


@dataclass
class Alien:
    """An alien (non-citizen) in immigration proceedings."""
    name: str
    alien_id: str
    nationality: str
    date_of_birth: date
    admission_class: Optional[AdmissionClass] = None
    date_of_entry: Optional[date] = None
    lpr_since: Optional[date] = None
    
    @property
    def age(self) -> int:
        """Calculate current age."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_lpr(self) -> bool:
        """Check if alien is Lawful Permanent Resident."""
        return self.admission_class == AdmissionClass.IMMIGRANT
    
    @property
    def years_as_lpr(self) -> Optional[int]:
        """Years as LPR (for naturalization eligibility)."""
        if self.lpr_since is None:
            return None
        return (date.today() - self.lpr_since).days // 365


@dataclass
class VisaApplication:
    """Application for immigration benefit."""
    application_id: str
    applicant: Alien
    visa_category: VisaCategory
    priority_date: Optional[date] = None
    filing_date: date = field(default_factory=date.today)
    approved: Optional[bool] = None
    
    def is_family_based(self) -> bool:
        """Check if family-sponsored category."""
        return self.visa_category in [
            VisaCategory.F1_FAMILY, VisaCategory.F2A, VisaCategory.F2B,
            VisaCategory.F3_FAMILY, VisaCategory.F4_FAMILY,
        ]
    
    def is_employment_based(self) -> bool:
        """Check if employment-based category."""
        return self.visa_category in [
            VisaCategory.EB1, VisaCategory.EB2, VisaCategory.EB3,
            VisaCategory.EB4, VisaCategory.EB5,
        ]


@dataclass
class AsylumClaim:
    """Asylum or withholding of removal claim."""
    claimant: Alien
    claim_date: date
    persecution_claims: List[Dict] = field(default_factory=list)
    feared_country: str = ""
    one_year_filing_deadline: date = field(default_factory=date.today)
    exceptions_to_deadline: List[str] = field(default_factory=list)
    
    def add_persecution_claim(
        self,
        harm: str,
        nexus: str,  # Race, religion, nationality, political opinion, particular social group
        government_involvement: bool,
    ):
        """Add a persecution claim with nexus to protected ground."""
        self.persecution_claims.append({
            "harm": harm,
            "nexus": nexus,
            "government_involvement": government_involvement,
        })
    
    def meets_filing_deadline(self) -> bool:
        """Check if claim filed within one year of entry."""
        if not self.claimant.date_of_entry:
            return False
        deadline = self.claimant.date_of_entry + timedelta(days=365)
        return self.claim_date <= deadline
    
    def has_protected_nexus(self) -> bool:
        """Check if any claim has nexus to protected ground."""
        protected_grounds = {
            "race", "religion", "nationality", "political opinion",
            "particular social group", "membership in a particular social group",
        }
        for claim in self.persecution_claims:
            if claim["nexus"].lower() in protected_grounds:
                return True
        return False


class VisaPreferenceSystem:
    """Implements visa preference and priority date system.
    
    The preference system allocates limited visa numbers across
    categories—reflecting ordered priorities set by Congress.
    """
    
    # Annual visa limits (simplified)
    FAMILY_TOTAL = 226_000
    EMPLOYMENT_TOTAL = 140_000
    
    # Per-country limits (7% of total)
    PER_COUNTRY_LIMIT = Fraction(7, 100)
    
    def __init__(self):
        self.visa_bulletin: Dict[VisaCategory, date] = {}
    
    def get_category_allocation(self, category: VisaCategory) -> int:
        """Get annual visa allocation for category."""
        allocations = {
            VisaCategory.F1_FAMILY: 23_400,
            VisaCategory.F2A: 21_984,
            VisaCategory.F2B: 26_266,
            VisaCategory.F3_FAMILY: 23_400,
            VisaCategory.F4_FAMILY: 65_000,
            VisaCategory.EB1: 40_040,
            VisaCategory.EB2: 40_040,
            VisaCategory.EB3: 40_040,
            VisaCategory.EB4: 9_940,
            VisaCategory.EB5: 9_940,
        }
        return allocations.get(category, 0)
    
    def is_visa_current(self, application: VisaApplication) -> bool:
        """Check if visa number available (priority date current)."""
        if application.priority_date is None:
            return True  # Immediate relative categories
        
        cutoff_date = self.visa_bulletin.get(application.visa_category)
        if cutoff_date is None:
            return True  # No backlog
        
        return application.priority_date <= cutoff_date
    
    def get_country_limit(self, category: VisaCategory) -> int:
        """Get per-country limit for category."""
        total = self.get_category_allocation(category)
        return int(total * self.PER_COUNTRY_LIMIT)


class AsylumAnalyzer:
    """Analyzer for asylum and withholding claims.
    
    Asylum reflects international obligations and the biblical
    command to care for the stranger (Leviticus 19:34: "The
    foreigner residing among you must be treated as your native-born").
    """
    
    def __init__(self):
        self.required_elements = [
            "persecution_or_fear",
            "on_account_of_protected_ground",
            "government_unwilling_or_unable",
        ]
    
    def analyze_asylum_eligibility(
        self,
        claim: AsylumClaim,
    ) -> Dict:
        """Analyze asylum claim eligibility.
        
        Args:
            claim: The asylum claim to analyze
            
        Returns:
            Eligibility analysis
        """
        analysis = {
            "claimant": claim.claimant.name,
            "eligible": True,
            "issues": [],
            "required_elements_met": {},
            "discretionary_factors": {},
        }
        
        # Check filing deadline
        deadline_met = claim.meets_filing_deadline()
        has_exceptions = len(claim.exceptions_to_deadline) > 0
        
        if not deadline_met and not has_exceptions:
            analysis["issues"].append("Failed to file within one year without exception")
            analysis["eligible"] = False
        
        # Check nexus to protected ground
        if not claim.has_protected_nexus():
            analysis["issues"].append("No nexus to protected ground established")
            analysis["eligible"] = False
        
        # Check persecution claims
        if not claim.persecution_claims:
            analysis["issues"].append("No persecution claims presented")
            analysis["eligible"] = False
        
        # Analyze each claim
        for i, persecution in enumerate(claim.persecution_claims):
            claim_analysis = self._analyze_persecution_claim(persecution)
            analysis["required_elements_met"][f"claim_{i+1}"] = claim_analysis
        
        # Check bars to asylum
        bars = self._check_asylum_bars(claim)
        analysis["bars"] = bars
        if bars:
            analysis["eligible"] = False
            analysis["issues"].extend([f"Bar: {b}" for b in bars])
        
        return analysis
    
    def _analyze_persecution_claim(self, claim: Dict) -> Dict:
        """Analyze individual persecution claim."""
        result = {
            "harm_established": len(claim["harm"]) > 0,
            "nexus_established": claim["nexus"] in [
                "race", "religion", "nationality", "political opinion",
                "particular social group",
            ],
            "government_actor": claim["government_involvement"],
        }
        
        result["well_founded_fear"] = (
            result["harm_established"] and
            result["nexus_established"]
        )
        
        return result
    
    def _check_asylum_bars(self, claim: AsylumClaim) -> List[str]:
        """Check for statutory bars to asylum."""
        bars = []
        
        # Persecutor of others bar (INA §208(b)(2)(A)(i))
        # (Would need additional data on applicant's history)
        
        # Particularly serious crime bar (INA §208(b)(2)(A)(ii))
        # (Would need criminal history)
        
        # Firm resettlement bar (INA §208(b)(2)(A)(vi))
        # (Would need information about third-country residence)
        
        return bars


class RemovalDefenseAnalyzer:
    """Analyzer for removal proceedings and defenses."""
    
    def __init__(self):
        self.deportation_defenses = [
            "cancellation_of_removal_lpr",
            "cancellation_of_removal_non_lpr",
            "adjustment_of_status",
            "asylum",
            "withholding",
            "cat_protection",  # Convention Against Torture
        ]
    
    def analyze_cancellation_eligibility(
        self,
        alien: Alien,
        years_residence: int,
        good_moral_character: bool,
        exceptional_hardship: bool,
    ) -> Dict:
        """Analyze eligibility for cancellation of removal.
        
        Cancellation of removal (formerly suspension) is a
        discretionary remedy for certain aliens in removal proceedings.
        
        Args:
            alien: The alien in proceedings
            years_residence: Years of continuous physical presence
            good_moral_character: Whether GMC established
            exceptional_hardship: Whether exceptional hardship to qualifying relative
            
        Returns:
            Eligibility analysis
        """
        analysis = {
            "relief_type": None,
            "eligible": False,
            "requirements_met": {},
            "requirements_failed": [],
        }
        
        if alien.is_lpr:
            # LPR cancellation (INA §240A(a))
            # 5 years as LPR, 7 years continuous residence, no aggravated felony
            analysis["relief_type"] = "cancellation_lpr"
            
            lpr_years = alien.years_as_lpr or 0
            analysis["requirements_met"]["lpr_5_years"] = lpr_years >= 5
            analysis["requirements_met"]["continuous_residence_7"] = years_residence >= 7
            analysis["requirements_met"]["good_moral_character"] = good_moral_character
            
            if all(analysis["requirements_met"].values()):
                analysis["eligible"] = True
            else:
                for req, met in analysis["requirements_met"].items():
                    if not met:
                        analysis["requirements_failed"].append(req)
        else:
            # Non-LPR cancellation (INA §240A(b)) - very limited
            # 10 years continuous physical presence, good moral character,
            # exceptional and extremely unusual hardship to USC/LPR spouse/parent/child
            analysis["relief_type"] = "cancellation_non_lpr"
            
            analysis["requirements_met"]["continuous_presence_10"] = years_residence >= 10
            analysis["requirements_met"]["good_moral_character"] = good_moral_character
            analysis["requirements_met"]["exceptional_hardship"] = exceptional_hardship
            
            if all(analysis["requirements_met"].values()):
                analysis["eligible"] = True
            else:
                for req, met in analysis["requirements_met"].items():
                    if not met:
                        analysis["requirements_failed"].append(req)
        
        return analysis
    
    def check_due_process_rights(self, alien: Alien, proceedings_pending: bool) -> Dict:
        """Check due process rights in removal proceedings.
        
        Links to Layer 1 constitutional protections—aliens in
        removal proceedings have Fifth Amendment due process rights.
        
        Args:
            alien: The alien in proceedings
            proceedings_pending: Whether removal proceedings active
            
        Returns:
            Due process rights analysis
        """
        rights = {
            "notice_rights": {
                "nta_received": proceedings_pending,  # Notice to Appear
                "charges_specified": proceedings_pending,
            },
            "hearing_rights": {
                "right_to_hearing": True,
                "right_to_counsel": True,  # At no expense to government
                "right_to_present_evidence": True,
                "right_to_cross_examine": True,
            },
            "appeal_rights": {
                "right_to_administrative_appeal": True,
                "right_to_judicial_review": True,
            },
        }
        
        # Children have additional protections
        if alien.age < 18:
            rights["special_protections"] = {
                "juvenile_docket": True,
                "custody_considerations": True,
                "sijs_eligible": alien.age < 21,  # Special Immigrant Juvenile Status
            }
        
        return rights


class ImmigrationComplianceChecker:
    """Comprehensive immigration law compliance checker."""
    
    def __init__(self):
        self.visa_system = VisaPreferenceSystem()
        self.asylum_analyzer = AsylumAnalyzer()
        self.removal_defense = RemovalDefenseAnalyzer()
    
    def check_visa_eligibility(self, application: VisaApplication) -> Dict:
        """Check visa application eligibility."""
        issues = []
        
        # Check if category has numerical limitation
        allocation = self.visa_system.get_category_allocation(application.visa_category)
        if allocation == 0 and not application.is_family_based():
            issues.append("Category has no visa allocation")
        
        # Check priority date
        current = self.visa_system.is_visa_current(application)
        if not current:
            issues.append("Priority date not current")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "visa_available": current,
            "category_allocation": allocation,
        }
    
    def check_asylum_compliance(self, claim: AsylumClaim) -> Dict:
        """Check asylum claim compliance."""
        analysis = self.asylum_analyzer.analyze_asylum_eligibility(claim)
        
        return {
            "compliant": analysis["eligible"] and len(analysis["issues"]) == 0,
            "issues": analysis["issues"],
            "analysis": analysis,
        }


def check_visa_category_eligibility(
    category: VisaCategory,
    priority_date: Optional[date],
    nationality: str,
) -> Dict:
    """Convenience function to check visa eligibility.
    
    Usage:
        result = check_visa_category_eligibility(
            category=VisaCategory.F1_FAMILY,
            priority_date=date(2020, 1, 15),
            nationality="Mexico",
        )
        print(f"Visa current: {result['current']}")
    """
    dummy_alien = Alien(
        name="Applicant",
        alien_id="A001",
        nationality=nationality,
        date_of_birth=date(1990, 1, 1),
    )
    
    application = VisaApplication(
        application_id="APP001",
        applicant=dummy_alien,
        visa_category=category,
        priority_date=priority_date,
    )
    
    system = VisaPreferenceSystem()
    
    return {
        "category": category.name,
        "allocation": system.get_category_allocation(category),
        "country_limit": system.get_country_limit(category),
        "current": system.is_visa_current(application),
        "family_based": application.is_family_based(),
        "employment_based": application.is_employment_based(),
    }
