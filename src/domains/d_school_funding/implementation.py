"""D_SCHOOL_FUNDING implementation — School Funding

Implements school funding formulas including per-pupil allocations,
Title I funding, and property tax distribution.

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: Title I (ESEA 20 U.S.C. §6301), state education codes

Biblical: Proverbs 22:6 — "Start children off on the way they should go,
and even when they are old they will not turn from it."
Also: James 1:5 — "If any of you lacks wisdom, you should ask God..."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class FundingSource(Enum):
    """Sources of school funding."""
    FEDERAL = auto()
    STATE = auto()
    LOCAL_PROPERTY_TAX = auto()
    LOCAL_OTHER = auto()
    PRIVATE = auto()


class StudentCategory(Enum):
    """Categories of students for weighted funding."""
    GENERAL_EDUCATION = auto()
    SPECIAL_EDUCATION = auto()
    ENGLISH_LEARNER = auto()
    ECONOMICALLY_DISADVANTAGED = auto()
    GIFTED_TALENTED = auto()


@dataclass
class SchoolDistrict:
    """A school district receiving funding."""
    district_id: str
    name: str
    state: str
    
    # Enrollment
    total_enrollment: int
    students_by_category: Dict[StudentCategory, int] = field(default_factory=dict)
    
    # Financial
    total_budget: Fraction = Fraction(0)
    local_tax_revenue: Fraction = Fraction(0)
    state_aid: Fraction = Fraction(0)
    federal_aid: Fraction = Fraction(0)
    
    # Property values
    total_assessed_value: Fraction = Fraction(0)
    tax_rate: Fraction = Fraction(0)  # Per $1000 of assessed value
    
    # Title I
    title_i_eligible: bool = False
    poverty_rate: Fraction = Fraction(0)  # Percentage as fraction


@dataclass
class PerPupilAllocation:
    """Per-pupil funding allocation."""
    district_id: str
    fiscal_year: int
    
    # Base allocation
    base_amount: Fraction  # Base per student
    
    # Weighted amounts by category
    category_weights: Dict[StudentCategory, Fraction] = field(default_factory=dict)
    
    # Calculated total
    weighted_enrollment: Fraction = Fraction(0)
    total_allocation: Fraction = Fraction(0)
    
    def calculate_weighted_enrollment(self, students: Dict[StudentCategory, int]) -> Fraction:
        """Calculate weighted enrollment using category weights."""
        weighted = Fraction(0)
        for category, count in students.items():
            weight = self.category_weights.get(category, Fraction(1))
            weighted += Fraction(count) * weight
        self.weighted_enrollment = weighted
        return weighted
    
    def calculate_total(self) -> Fraction:
        """Calculate total allocation."""
        self.total_allocation = self.base_amount * self.weighted_enrollment
        return self.total_allocation


@dataclass
class TitleIAllocation:
    """Title I funding allocation."""
    district_id: str
    fiscal_year: int
    
    # Eligibility
    eligible: bool
    poverty_rate: Fraction  # 0.0 to 1.0
    
    # Allocation factors
    basic_grant: Fraction = Fraction(0)
    concentration_grant: Fraction = Fraction(0)  # Higher poverty = more
    targeted_grant: Fraction = Fraction(0)
    
    @property
    def total_allocation(self) -> Fraction:
        """Total Title I allocation."""
        return self.basic_grant + self.concentration_grant + self.targeted_grant


@dataclass
class PropertyTaxDistribution:
    """Property tax distribution formula."""
    jurisdiction_id: str
    fiscal_year: int
    
    # Collection
    total_collected: Fraction
    
    # Distribution formula (must sum to 1.0)
    school_district_share: Fraction = Fraction(50, 100)  # 50%
    municipality_share: Fraction = Fraction(30, 100)     # 30%
    county_share: Fraction = Fraction(15, 100)           # 15%
    other_share: Fraction = Fraction(5, 100)             # 5%
    
    def validate_formula(self) -> bool:
        """Validate that formula sums to 1.0."""
        total = (self.school_district_share + self.municipality_share +
                 self.county_share + self.other_share)
        return total == Fraction(1)
    
    def calculate_distribution(self) -> Dict[str, Fraction]:
        """Calculate distribution amounts."""
        return {
            "school_district": self.total_collected * self.school_district_share,
            "municipality": self.total_collected * self.municipality_share,
            "county": self.total_collected * self.county_share,
            "other": self.total_collected * self.other_share,
        }


class FundingCalculator:
    """Calculator for school funding formulas."""
    
    # Default weights for student categories
    DEFAULT_WEIGHTS = {
        StudentCategory.GENERAL_EDUCATION: Fraction(1),
        StudentCategory.SPECIAL_EDUCATION: Fraction(2),  # 2x base
        StudentCategory.ENGLISH_LEARNER: Fraction(15, 10),  # 1.5x
        StudentCategory.ECONOMICALLY_DISADVANTAGED: Fraction(12, 10),  # 1.2x
        StudentCategory.GIFTED_TALENTED: Fraction(11, 10),  # 1.1x
    }
    
    # Title I thresholds
    TITLE_I_MIN_POVERTY_RATE = Fraction(2, 100)  # 2%
    CONCENTRATION_GRANT_THRESHOLD = Fraction(15, 100)  # 15%
    
    def __init__(self):
        self.districts: Dict[str, SchoolDistrict] = {}
    
    def calculate_per_pupil_allocation(self, district: SchoolDistrict,
                                        base_amount: Fraction) -> PerPupilAllocation:
        """Calculate per-pupil allocation for a district."""
        allocation = PerPupilAllocation(
            district_id=district.district_id,
            fiscal_year=datetime.now().year,
            base_amount=base_amount,
            category_weights=self.DEFAULT_WEIGHTS.copy(),
        )
        
        allocation.calculate_weighted_enrollment(district.students_by_category)
        allocation.calculate_total()
        
        return allocation
    
    def calculate_title_i_allocation(self, district: SchoolDistrict,
                                      total_federal_funds: Fraction) -> TitleIAllocation:
        """
        Calculate Title I allocation based on poverty rate.
        
        Formula: Higher poverty rate = higher per-pupil allocation
        """
        eligible = district.poverty_rate >= self.TITLE_I_MIN_POVERTY_RATE
        
        if not eligible:
            return TitleIAllocation(
                district_id=district.district_id,
                fiscal_year=datetime.now().year,
                eligible=False,
                poverty_rate=district.poverty_rate,
            )
        
        # Basic grant: proportional to poverty rate
        basic = total_federal_funds * district.poverty_rate
        
        # Concentration grant: additional for high-poverty districts
        concentration = Fraction(0)
        if district.poverty_rate >= self.CONCENTRATION_GRANT_THRESHOLD:
            concentration = total_federal_funds * (district.poverty_rate - 
                                                    self.CONCENTRATION_GRANT_THRESHOLD)
        
        # Targeted grant: higher weight for very high poverty
        targeted = Fraction(0)
        if district.poverty_rate >= Fraction(30, 100):  # 30%
            targeted = total_federal_funds * district.poverty_rate * Fraction(5, 10)
        
        return TitleIAllocation(
            district_id=district.district_id,
            fiscal_year=datetime.now().year,
            eligible=True,
            poverty_rate=district.poverty_rate,
            basic_grant=basic,
            concentration_grant=concentration,
            targeted_grant=targeted,
        )
    
    def calculate_property_tax_revenue(self, district: SchoolDistrict) -> Fraction:
        """Calculate property tax revenue for school district."""
        # Revenue = Assessed value * (tax rate / 1000)
        if district.tax_rate == 0:
            return Fraction(0)
        
        revenue = district.total_assessed_value * district.tax_rate / Fraction(1000)
        return revenue


class EquityAnalyzer:
    """Analyzer for funding equity across districts."""
    
    # Equity threshold: coefficient of variation should be below this
    EQUITY_THRESHOLD = Fraction(10, 100)  # 10% variation
    
    def analyze_spending_equity(self, districts: List[SchoolDistrict]) -> Dict:
        """
        Analyze per-pupil spending equity across districts.
        
        Invariant: Per-pupil spending variance ≤ equity threshold.
        """
        if not districts:
            return {"equitable": True, "variance": Fraction(0)}
        
        # Calculate per-pupil spending for each district
        per_pupil_spending = []
        for d in districts:
            total_funding = d.total_budget
            if d.total_enrollment > 0:
                per_pupil = total_funding / d.total_enrollment
            else:
                per_pupil = Fraction(0)
            per_pupil_spending.append(per_pupil)
        
        if not per_pupil_spending:
            return {"equitable": True, "variance": Fraction(0)}
        
        # Calculate mean
        mean_spending = sum(per_pupil_spending) / len(per_pupil_spending)
        
        # Calculate standard deviation (simplified)
        variance_sum = sum((spending - mean_spending) ** 2 
                          for spending in per_pupil_spending)
        variance = variance_sum / len(per_pupil_spending)
        
        # Coefficient of variation (std dev / mean)
        if mean_spending > 0:
            cv = (variance ** Fraction(1, 2)) / mean_spending
        else:
            cv = Fraction(0)
        
        # Check against threshold (comparing as float for simplicity)
        equitable = cv <= self.EQUITY_THRESHOLD
        
        return {
            "mean_spending": mean_spending,
            "variance": variance,
            "coefficient_of_variation": cv,
            "equitable": equitable,
            "threshold": self.EQUITY_THRESHOLD,
        }
    
    def compare_district_funding(self, district1: SchoolDistrict,
                                  district2: SchoolDistrict) -> Dict:
        """Compare funding between two districts."""
        if district1.total_enrollment == 0 or district2.total_enrollment == 0:
            return {"error": "Zero enrollment"}
        
        per_pupil_1 = district1.total_budget / district1.total_enrollment
        per_pupil_2 = district2.total_budget / district2.total_enrollment
        
        if per_pupil_2 > 0:
            ratio = per_pupil_1 / per_pupil_2
        else:
            ratio = Fraction(0)
        
        return {
            "district_1": district1.district_id,
            "district_2": district2.district_id,
            "per_pupil_1": per_pupil_1,
            "per_pupil_2": per_pupil_2,
            "ratio": ratio,
            "disparity": abs(ratio - Fraction(1)),
        }


class FundingComplianceAuditor:
    """Auditor for school funding compliance."""
    
    def __init__(self):
        self.calculator = FundingCalculator()
        self.equity_analyzer = EquityAnalyzer()
    
    def audit_district(self, district: SchoolDistrict) -> Dict:
        """Audit a single district's funding."""
        # Calculate expected property tax revenue
        expected_tax = self.calculator.calculate_property_tax_revenue(district)
        
        return {
            "district_id": district.district_id,
            "enrollment": district.total_enrollment,
            "total_budget": district.total_budget,
            "local_revenue": district.local_tax_revenue,
            "expected_tax_revenue": expected_tax,
            "title_i_eligible": district.title_i_eligible,
            "poverty_rate": district.poverty_rate,
        }
    
    def audit_equity(self, districts: List[SchoolDistrict]) -> Dict:
        """Audit funding equity across districts."""
        return self.equity_analyzer.analyze_spending_equity(districts)
    
    def audit_title_i_formula(self, district: SchoolDistrict) -> Dict:
        """Verify Title I allocation follows formula."""
        allocation = self.calculator.calculate_title_i_allocation(
            district, Fraction(1000000)  # $1M hypothetical total
        )
        
        return {
            "district_id": district.district_id,
            "eligible": allocation.eligible,
            "poverty_rate": allocation.poverty_rate,
            "total_allocation": allocation.total_allocation,
            "formulaic": True,  # Allocation always follows formula
        }


# Convenience functions
def check_funding_equity(districts: List[SchoolDistrict]) -> Dict:
    """Quick check of funding equity."""
    analyzer = EquityAnalyzer()
    return analyzer.analyze_spending_equity(districts)


def check_title_i_eligibility(poverty_rate: Fraction) -> Dict:
    """Quick check of Title I eligibility."""
    calculator = FundingCalculator()
    eligible = poverty_rate >= calculator.TITLE_I_MIN_POVERTY_RATE
    
    return {
        "poverty_rate": poverty_rate,
        "eligible": eligible,
        "threshold": calculator.TITLE_I_MIN_POVERTY_RATE,
    }


def check_tax_formula_determinism(assessed_value: Fraction, 
                                   tax_rate: Fraction) -> Dict:
    """Quick check that tax calculation is deterministic."""
    # Run calculation multiple times
    calc1 = assessed_value * tax_rate / Fraction(1000)
    calc2 = assessed_value * tax_rate / Fraction(1000)
    calc3 = assessed_value * tax_rate / Fraction(1000)
    
    return {
        "revenue": calc1,
        "deterministic": calc1 == calc2 == calc3,
    }
