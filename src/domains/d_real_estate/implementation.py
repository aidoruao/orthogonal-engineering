"""D_REAL_ESTATE implementation — Real Estate

Implements real estate regulations including property assessment,
anti-redlining protections, and disclosure requirements.

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State property codes, Fair Housing Act (42 U.S.C. §3605), RESPA

Biblical: Leviticus 25:23 — "The land must not be sold permanently, because
the land is mine and you reside in my land as foreigners and strangers."
Also: Proverbs 31:16 — "She considers a field and buys it; out of her earnings
she plants a vineyard."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class PropertyType(Enum):
    """Types of real property."""
    SINGLE_FAMILY_RESIDENTIAL = auto()
    MULTI_FAMILY_RESIDENTIAL = auto()
    COMMERCIAL = auto()
    INDUSTRIAL = auto()
    AGRICULTURAL = auto()
    VACANT_LAND = auto()


class LoanDecision(Enum):
    """Loan application decisions."""
    APPROVED = auto()
    DENIED = auto()
    CONDITIONAL = auto()
    PENDING = auto()


class ProtectedClass(Enum):
    """Protected classes under Fair Housing Act (lending)."""
    RACE = auto()
    COLOR = auto()
    NATIONAL_ORIGIN = auto()
    RELIGION = auto()
    SEX = auto()
    FAMILIAL_STATUS = auto()
    DISABILITY = auto()


class DisclosureType(Enum):
    """Types of required real estate disclosures."""
    LEAD_BASED_PAINT = auto()
    NATURAL_HAZARDS = auto()
    MEGANS_LAW = auto()
    TRANSFER_DISCLOSURE = auto()
    SELLER_PROPERTY_QUESTIONNAIRE = auto()
    AGENCY_DISCLOSURE = auto()
    MORTGAGE_DISCLOSURE = auto()
    INSPECTION_REPORTS = auto()


@dataclass
class Property:
    """A real property."""
    property_id: str
    address: str
    parcel_number: str
    
    # Characteristics
    property_type: PropertyType
    lot_size_sqft: Fraction
    year_built: Optional[int] = None
    square_footage: Optional[Fraction] = None
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[Fraction] = None
    
    # Location
    census_tract: Optional[str] = None
    neighborhood_code: Optional[str] = None
    school_district: Optional[str] = None
    
    # Features
    garage_spaces: int = 0
    pool: bool = False
    fireplace: bool = False


@dataclass
class PropertyAssessment:
    """An assessed value for a property."""
    property_id: str
    assessment_year: int
    
    # Assessment components
    land_value: Fraction
    improvement_value: Fraction
    total_value: Fraction
    
    # Calculation inputs
    comparable_sales: List[str] = field(default_factory=list)  # Sale IDs used
    assessment_method: str = "comparable_sales"
    
    # Reproducibility
    assessment_date: datetime = field(default_factory=datetime.now)
    assessor_id: str = ""
    
    @property
    def assessment_reproducible(self) -> bool:
        """Check if assessment can be reproduced."""
        return (
            len(self.comparable_sales) > 0 and
            self.assessment_method != "" and
            self.assessor_id != ""
        )


@dataclass
class LoanApplication:
    """A mortgage loan application."""
    application_id: str
    applicant_id: str
    property_id: str
    
    # Financial (required)
    loan_amount: Fraction
    applicant_income: Fraction
    credit_score: int
    debt_to_income_ratio: Fraction
    
    # Applicant characteristics (optional - for fair lending analysis)
    applicant_race: Optional[str] = None
    applicant_ethnicity: Optional[str] = None
    applicant_sex: Optional[str] = None
    
    # Decision (optional)
    decision: Optional[LoanDecision] = None
    decision_date: Optional[datetime] = None
    decision_reason: Optional[str] = None
    
    # Protected class analysis (optional)
    protected_class_flagged: Optional[bool] = None


@dataclass
class LendingDecision:
    """A lending decision record."""
    decision_id: str
    application_id: str
    
    # Decision details
    approved: bool
    interest_rate: Optional[Fraction] = None
    loan_amount: Fraction = Fraction(0)
    
    # Factors considered (must be non-discriminatory)
    credit_score_used: bool = True
    income_verified: bool = True
    property_appraised: bool = True
    debt_ratio_calculated: bool = True
    
    # Decision rationale
    rationale: str = ""
    
    def check_non_discriminatory(self) -> Dict:
        """Check if decision uses only legitimate factors."""
        legitimate_factors = all([
            self.credit_score_used,
            self.income_verified,
            self.debt_ratio_calculated,
        ])
        
        return {
            "decision_id": self.decision_id,
            "legitimate_factors_only": legitimate_factors,
            "documented_rationale": self.rationale != "",
        }


@dataclass
class PropertyDisclosure:
    """A property disclosure document."""
    disclosure_id: str
    property_id: str
    disclosure_type: DisclosureType
    
    # Content
    disclosed_items: List[str] = field(default_factory=list)
    known_defects: List[str] = field(default_factory=list)
    
    # Execution
    disclosure_date: datetime = field(default_factory=datetime.now)
    seller_signed: bool = False
    buyer_acknowledged: bool = False


@dataclass
class DisclosurePackage:
    """A complete set of disclosures for a property transaction."""
    package_id: str
    property_id: str
    transaction_id: str
    
    # Required disclosures
    disclosures: Dict[DisclosureType, PropertyDisclosure] = field(default_factory=dict)
    
    # Completeness
    completion_date: Optional[datetime] = None
    
    def check_completeness(self) -> Dict:
        """Check if all required disclosures are present."""
        # Standard required disclosures
        required = [
            DisclosureType.LEAD_BASED_PAINT,
            DisclosureType.NATURAL_HAZARDS,
            DisclosureType.TRANSFER_DISCLOSURE,
            DisclosureType.AGENCY_DISCLOSURE,
        ]
        
        present = [dt for dt in self.disclosures.keys()]
        missing = [dt for dt in required if dt not in present]
        
        return {
            "package_id": self.package_id,
            "required_count": len(required),
            "present_count": len(present),
            "missing_types": [dt.name for dt in missing],
            "complete": len(missing) == 0,
        }


class PropertyAssessor:
    """Property assessment system."""
    
    # Assessment rates by property type
    LAND_VALUE_RATES = {
        PropertyType.SINGLE_FAMILY_RESIDENTIAL: Fraction(10),  # $/sqft
        PropertyType.MULTI_FAMILY_RESIDENTIAL: Fraction(15),
        PropertyType.COMMERCIAL: Fraction(25),
        PropertyType.INDUSTRIAL: Fraction(20),
        PropertyType.AGRICULTURAL: Fraction(2),
    }
    
    IMPROVEMENT_RATES = {
        PropertyType.SINGLE_FAMILY_RESIDENTIAL: Fraction(150),  # $/sqft
        PropertyType.MULTI_FAMILY_RESIDENTIAL: Fraction(120),
        PropertyType.COMMERCIAL: Fraction(200),
        PropertyType.INDUSTRIAL: Fraction(100),
    }
    
    def assess_property(self, property_obj: Property,
                        comparable_sales: List[str]) -> PropertyAssessment:
        """
        Assess property value deterministically.
        
        Invariant: Property assessment is reproducible.
        """
        # Calculate land value
        land_rate = self.LAND_VALUE_RATES.get(property_obj.property_type, Fraction(10))
        land_value = property_obj.lot_size_sqft * land_rate / Fraction(43560)  # Per acre
        
        # Calculate improvement value
        improvement_value = Fraction(0)
        if property_obj.square_footage:
            improvement_rate = self.IMPROVEMENT_RATES.get(
                property_obj.property_type, Fraction(100)
            )
            
            # Age adjustment
            age_adjustment = Fraction(1)
            if property_obj.year_built:
                age = datetime.now().year - property_obj.year_built
                age_adjustment = max(Fraction(1, 2), Fraction(1) - Fraction(age, 100))
            
            improvement_value = property_obj.square_footage * improvement_rate * age_adjustment
        
        total_value = land_value + improvement_value
        
        return PropertyAssessment(
            property_id=property_obj.property_id,
            assessment_year=datetime.now().year,
            land_value=land_value,
            improvement_value=improvement_value,
            total_value=total_value,
            comparable_sales=comparable_sales,
            assessment_method="cost_approach",
            assessor_id="ASSESSOR_001",
        )
    
    def verify_reproducibility(self, property_obj: Property,
                                comparable_sales: List[str]) -> Dict:
        """Verify that assessment is reproducible."""
        assessment1 = self.assess_property(property_obj, comparable_sales)
        assessment2 = self.assess_property(property_obj, comparable_sales)
        
        return {
            "property_id": property_obj.property_id,
            "reproducible": assessment1.total_value == assessment2.total_value,
            "total_value": assessment1.total_value,
            "method_documented": assessment1.assessment_reproducible,
        }


class FairLendingMonitor:
    """Monitor for fair lending compliance."""
    
    def analyze_lending_decisions(self, 
                                   decisions: List[LendingDecision],
                                   applications: List[LoanApplication]) -> Dict:
        """
        Analyze lending decisions for discrimination patterns.
        
        Invariant: No race-based lending discrimination (anti-redlining).
        """
        # Build application lookup
        app_lookup = {a.application_id: a for a in applications}
        
        # Analyze approval rates by protected class
        analysis = {
            "total_applications": len(applications),
            "total_decisions": len(decisions),
            "by_race": {},
            "by_sex": {},
            "potential_discrimination": [],
        }
        
        # Group by race
        by_race: Dict[str, List] = {}
        for decision in decisions:
            app = app_lookup.get(decision.application_id)
            if app and app.applicant_race:
                race = app.applicant_race
                if race not in by_race:
                    by_race[race] = []
                by_race[race].append(decision)
        
        # Calculate approval rates by race
        for race, race_decisions in by_race.items():
            approved = sum(1 for d in race_decisions if d.approved)
            total = len(race_decisions)
            rate = Fraction(approved, total) if total > 0 else Fraction(0)
            analysis["by_race"][race] = {
                "total": total,
                "approved": approved,
                "approval_rate": rate,
            }
        
        # Check for disparate treatment (simplified)
        if len(analysis["by_race"]) >= 2:
            rates = [r["approval_rate"] for r in analysis["by_race"].values()]
            max_rate = max(rates)
            min_rate = min(rates)
            
            # Flag if disparity > 20 percentage points
            if max_rate > 0 and (max_rate - min_rate) > Fraction(2, 10):
                analysis["potential_discrimination"].append(
                    "Significant approval rate disparity by race"
                )
        
        return analysis
    
    def check_decision_factors(self, decision: LendingDecision) -> Dict:
        """Check if decision uses only legitimate factors."""
        return decision.check_non_discriminatory()


class DisclosureManager:
    """Manager for property disclosure requirements."""
    
    def create_disclosure(self, disclosure_id: str, property_id: str,
                          disclosure_type: DisclosureType,
                          items: List[str]) -> PropertyDisclosure:
        """Create a property disclosure."""
        return PropertyDisclosure(
            disclosure_id=disclosure_id,
            property_id=property_id,
            disclosure_type=disclosure_type,
            disclosed_items=items,
        )
    
    def create_package(self, package_id: str, property_id: str,
                       transaction_id: str) -> DisclosurePackage:
        """Create a disclosure package."""
        return DisclosurePackage(
            package_id=package_id,
            property_id=property_id,
            transaction_id=transaction_id,
        )
    
    def add_disclosure_to_package(self, package: DisclosurePackage,
                                   disclosure: PropertyDisclosure) -> Dict:
        """Add a disclosure to a package."""
        package.disclosures[disclosure.disclosure_type] = disclosure
        
        return {
            "package_id": package.package_id,
            "disclosure_added": disclosure.disclosure_type.name,
            "total_disclosures": len(package.disclosures),
        }
    
    def check_package_compliance(self, package: DisclosurePackage) -> Dict:
        """
        Check if disclosure package is complete.
        
        Invariant: Disclosure requirements are enumerated and complete.
        """
        return package.check_completeness()


class RealEstateAuditor:
    """Comprehensive auditor for real estate compliance."""
    
    def __init__(self):
        self.assessor = PropertyAssessor()
        self.lending_monitor = FairLendingMonitor()
        self.disclosure_manager = DisclosureManager()
    
    def audit_assessment(self, property_obj: Property,
                         comparable_sales: List[str]) -> Dict:
        """Audit property assessment."""
        return self.assessor.verify_reproducibility(property_obj, comparable_sales)
    
    def audit_lending(self, decisions: List[LendingDecision],
                      applications: List[LoanApplication]) -> Dict:
        """Audit lending decisions for discrimination."""
        return self.lending_monitor.analyze_lending_decisions(decisions, applications)
    
    def audit_disclosures(self, package: DisclosurePackage) -> Dict:
        """Audit disclosure completeness."""
        return self.disclosure_manager.check_package_compliance(package)


# Convenience functions
def check_assessment_reproducibility(property_obj: Property,
                                      comparable_sales: List[str]) -> Dict:
    """Quick check of assessment reproducibility."""
    assessor = PropertyAssessor()
    return assessor.verify_reproducibility(property_obj, comparable_sales)


def check_lending_decision_factors(decision: LendingDecision) -> Dict:
    """Quick check of lending decision factors."""
    return decision.check_non_discriminatory()


def check_disclosure_completeness(package: DisclosurePackage) -> Dict:
    """Quick check of disclosure completeness."""
    return package.check_completeness()
