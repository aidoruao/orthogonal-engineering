"""D_NEIGHBORHOOD_EQUITY implementation — Housing Equity, Redlining, Access

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: Fair Housing Act, Community Reinvestment Act, AFFH
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from fractions import Fraction


class NeighborhoodType(Enum):
    """Neighborhood classification types."""
    URBAN_CORE = auto()
    SUBURBAN = auto()
    RURAL = auto()
    TRANSITIONAL = auto()


@dataclass
class Neighborhood:
    """Neighborhood demographic and equity data."""
    neighborhood_id: str
    name: str
    neighborhood_type: NeighborhoodType
    
    # Population (Fraction for precision)
    total_population: Fraction
    minority_population: Fraction
    low_income_population: Fraction
    
    # Housing
    total_housing_units: Fraction
    affordable_housing_units: Fraction
    vacant_units: Fraction
    
    # Services access (minutes as Fraction)
    avg_transit_time_to_jobs: Fraction
    grocery_access_score: Fraction  # 0-1 scale
    healthcare_access_score: Fraction  # 0-1 scale
    school_quality_score: Fraction  # 0-1 scale
    
    # Lending data
    mortgage_applications: int
    mortgage_denials: int
    mortgage_denial_rate_minority: Fraction
    mortgage_denial_rate_non_minority: Fraction
    
    def get_affordability_ratio(self) -> Fraction:
        """Calculate affordable housing ratio."""
        if self.total_housing_units == 0:
            return Fraction(0)
        return self.affordable_housing_units / self.total_housing_units
    
    def get_disparate_impact_ratio(self) -> Fraction:
        """Calculate lending disparate impact ratio."""
        if self.mortgage_denial_rate_non_minority == 0:
            return Fraction(0)
        return self.mortgage_denial_rate_minority / self.mortgage_denial_rate_non_minority


@dataclass
class LendingInstitution:
    """Bank or lending institution CRA/Fair Housing data."""
    institution_id: str
    name: str
    
    # CRA assessment area
    assessment_area_population: Fraction
    low_mod_income_population: Fraction
    
    # Lending activity
    home_purchase_loans: int
    home_purchase_to_low_mod: int
    refinancing_loans: int
    refinancing_to_low_mod: int
    
    # Branch presence
    branches_in_low_mod_tracts: int
    total_branches: int
    
    def get_cra_loan_ratio(self) -> Fraction:
        """Calculate ratio of loans to low/moderate income borrowers."""
        total_loans = self.home_purchase_loans + self.refinancing_loans
        low_mod_loans = self.home_purchase_to_low_mod + self.refinancing_to_low_mod
        if total_loans == 0:
            return Fraction(0)
        return Fraction(low_mod_loans, total_loans)
    
    def get_branch_equity_ratio(self) -> Fraction:
        """Calculate ratio of branches in low/mod income areas."""
        if self.total_branches == 0:
            return Fraction(0)
        return Fraction(self.branches_in_low_mod_tracts, self.total_branches)


# Regulatory thresholds
FAIR_HOUSING_DISPARATE_IMPACT_THRESHOLD = Fraction(4, 3)  # 4/5 rule = 1.25, but we use 4/3 for stricter
cRA_LOW_MOD_INCOME_PERCENTAGE = Fraction(51, 100)  # 51%
AFFORDABLE_HOUSING_TARGET = Fraction(1, 10)  # 10% target


def fair_housing_disparate_impact_threshold() -> Fraction:
    """Fair Housing Act disparate impact threshold (80% rule)."""
    return Fraction(4, 5)  # 0.8


def cra_low_mod_threshold() -> Fraction:
    """CRA low/moderate income threshold percentage."""
    return CRA_LOW_MOD_INCOME_PERCENTAGE
