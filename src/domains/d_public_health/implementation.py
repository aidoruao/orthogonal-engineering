"""D_PUBLIC_HEALTH implementation — Public Health, Epidemiology, Disease Control

Layer: 3 (Health Regulation)
CardinalStrength: PREDICATIVE
Source: Public Health Service Act, CDC guidelines, WHO IHR
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum, auto
from fractions import Fraction


class DiseaseSeverity(Enum):
    """Disease severity classification."""
    MILD = auto()
    MODERATE = auto()
    SEVERE = auto()
    CRITICAL = auto()


class InterventionType(Enum):
    """Public health intervention."""
    VACCINATION = auto()
    SCREENING = auto()
    QUARANTINE = auto()
    CONTACT_TRACING = auto()
    HEALTH_EDUCATION = auto()


@dataclass
class DiseaseOutbreak:
    """Infectious disease outbreak."""
    outbreak_id: str
    disease_name: str
    severity: DiseaseSeverity
    
    # Cases
    cases_confirmed: int
    cases_probable: int
    deaths: int
    recoveries: int
    
    # Population
    population_at_risk: Fraction
    population_vaccinated: Fraction
    
    # Response
    r_naught_estimate: Fraction  # Reproduction number
    intervention_deployed: List[InterventionType]
    
    def get_case_fatality_rate(self) -> Fraction:
        """Calculate case fatality rate."""
        total_cases = self.cases_confirmed + self.cases_probable
        if total_cases == 0:
            return Fraction(0)
        return Fraction(self.deaths, total_cases)
    
    def get_vaccination_coverage(self) -> Fraction:
        """Calculate vaccination coverage."""
        return self.population_vaccinated / self.population_at_risk


@dataclass
class PublicHealthProgram:
    """Public health intervention program."""
    program_id: str
    intervention_type: InterventionType
    target_population: Fraction
    
    # Coverage
    people_reached: Fraction
    interventions_delivered: int
    
    # Effectiveness
    coverage_target: Fraction
    effectiveness_estimate: Fraction  # 0-1
    
    # Resources
    budget_allocated: Fraction
    budget_spent: Fraction
    
    def get_coverage_rate(self) -> Fraction:
        """Calculate coverage rate."""
        if self.target_population == 0:
            return Fraction(0)
        return self.people_reached / self.target_population
    
    def get_budget_utilization(self) -> Fraction:
        """Calculate budget utilization."""
        if self.budget_allocated == 0:
            return Fraction(0)
        return self.budget_spent / self.budget_allocated


# Public health standards
HERD_IMMUNITY_THRESHOLD = Fraction(95, 100)  # 95% for most diseases
MAX_ACCEPTABLE_CFR = Fraction(1, 10)  # 10% CFR intervention trigger
MIN_PROGRAM_COVERAGE = Fraction(8, 10)  # 80%


def herd_immunity_threshold() -> Fraction:
    """Herd immunity vaccination threshold."""
    return HERD_IMMUNITY_THRESHOLD


def max_acceptable_cfr() -> Fraction:
    """Maximum acceptable case fatality rate."""
    return MAX_ACCEPTABLE_CFR
