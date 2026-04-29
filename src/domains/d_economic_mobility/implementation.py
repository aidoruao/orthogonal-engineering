"""D_ECONOMIC_MOBILITY implementation — Economic Mobility & Opportunity

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Regulatory Standards:
- Equal Credit Opportunity Act (ECOA) 15 U.S.C. 1691
- Fair Housing Act 42 U.S.C. 3601
- Community Reinvestment Act (CRA) 12 U.S.C. 2901
- Workforce Innovation and Opportunity Act (WIOA)
- OECD Skills for Jobs indicators
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class MobilityDimension(Enum):
    """Dimensions of economic mobility measurement."""
    INCOME = auto()
    WEALTH = auto()
    EDUCATION = auto()
    OCCUPATION = auto()
    GEOGRAPHIC = auto()


class InterventionType(Enum):
    """Types of mobility-enhancing interventions."""
    JOB_TRAINING = auto()
    EDUCATION_SUBSIDY = auto()
    HOUSING_VOUCHER = auto()
    CHILD_SAVINGS = auto()
    TRANSPORTATION = auto()
    MENTORSHIP = auto()


@dataclass(frozen=True)
class QuintilePosition:
    """Position in income/wealth distribution quintiles (1=bottom, 5=top)."""
    parent_quintile: int  # 1-5
    child_quintile: int   # 1-5
    
    def absolute_mobility(self) -> bool:
        """True if child in higher quintile than parent."""
        return self.child_quintile > self.parent_quintile
    
    def quintile_change(self) -> int:
        """Positive if upward, negative if downward."""
        # TODO: Expand quintile_change() - stub detected by Yeshua Agent
        return self.child_quintile - self.parent_quintile


@dataclass
class MobilityMatrix:
    """Intergenerational mobility matrix by quintile transitions."""
    region: str
    year: int
    transitions: Dict[Tuple[int, int], Fraction]  # (parent, child) -> probability
    sample_size: int
    
    def probability_upward(self, from_quintile: int) -> Fraction:
        """Probability of upward mobility from given quintile."""
        total = Fraction(0)
        for child_q in range(from_quintile + 1, 6):
            total += self.transitions.get((from_quintile, child_q), Fraction(0))
        return total
    
    def stickiness_ratio(self) -> Fraction:
        """Fraction staying in same quintile vs expected (1/5)."""
        same_quintile = sum(
            self.transitions.get((q, q), Fraction(0))
            for q in range(1, 6)
        )
        expected = Fraction(1, 5)  # 20% random
        return same_quintile / expected if expected > 0 else Fraction(0)


@dataclass
class OpportunityAtlas:
    """Chetty et al. Opportunity Atlas data for a geography."""
    tract_id: str
    state: str
    county: str
    household_income_at_35: Fraction  # Mean income at age 35
    incarceration_rate: Fraction
    teenage_birth_rate: Fraction
    high_school_graduation_rate: Fraction
    college_attendance_rate: Fraction
    
    def opportunity_score(self) -> Fraction:
        """Composite opportunity score (0-100 scale)."""
        income_component = min(Fraction(household_income_at_35, 1000), Fraction(40))
        education_component = college_attendance_rate * Fraction(30)
        incarceration_penalty = incarceration_rate * Fraction(-100)
        
        score = income_component + education_component + incarceration_penalty
        return max(Fraction(0), min(Fraction(100), score))


@dataclass
class Intervention:
    """Economic mobility intervention program."""
    program_id: str
    name: str
    intervention_type: InterventionType
    target_population_size: int
    start_date: datetime
    cost_per_participant: Fraction
    
    def total_program_cost(self) -> Fraction:
        """Total program cost."""
        # TODO: Expand total_program_cost() - stub detected by Yeshua Agent
        return Fraction(self.target_population_size) * self.cost_per_participant


@dataclass
class InterventionOutcome:
    """Measured outcomes of an intervention."""
    intervention: Intervention
    follow_up_years: int
    participants_reached: int
    earnings_increase_annual: Fraction
    employment_rate_change: Fraction
    
    def cost_effectiveness(self) -> Fraction:
        """Return per dollar invested (social return)."""
        total_cost = self.intervention.total_program_cost()
        if total_cost == 0:
            return Fraction(0)
        
        # Lifetime earnings increase (simplified 20-year horizon)
        lifetime_gain = self.earnings_increase_annual * Fraction(20)
        return lifetime_gain / total_cost
    
    def completion_rate(self) -> Fraction:
        """Fraction of target population that completed program."""
        if self.intervention.target_population_size == 0:
            return Fraction(0)
        return Fraction(self.participants_reached, self.intervention.target_population_size)


@dataclass
class CreditAccessMetrics:
    """Credit access and fairness metrics per ECOA."""
    institution: str
    reporting_period: str
    total_applications: int
    approved_applications: int
    
    # Denial rates by protected class (ECOA protected characteristics)
    denial_rate_overall: Fraction
    denial_rate_by_race: Dict[str, Fraction]
    denial_rate_by_gender: Dict[str, Fraction]
    denial_rate_by_age: Dict[str, Fraction]
    
    def disparity_ratio(self, baseline: str, comparison: str) -> Optional[Fraction]:
        """Ratio of denial rates between groups (disparity detection)."""
        if baseline not in self.denial_rate_by_race or comparison not in self.denial_rate_by_race:
            return None
        base_rate = self.denial_rate_by_race[baseline]
        comp_rate = self.denial_rate_by_race[comparison]
        if base_rate == 0:
            return None
        return comp_rate / base_rate


@dataclass
class MobilityChecker:
    """Checker for economic mobility metrics and interventions."""
    matrices: List[MobilityMatrix] = field(default_factory=list)
    atlases: List[OpportunityAtlas] = field(default_factory=list)
    interventions: List[InterventionOutcome] = field(default_factory=list)
    credit_metrics: List[CreditAccessMetrics] = field(default_factory=list)
    
    def find_matrix(self, region: str, year: int) -> Optional[MobilityMatrix]:
        """Find mobility matrix for region and year."""
        for m in self.matrices:
            if m.region == region and m.year == year:
                return m
        return None
    
    def low_opportunity_tracts(self, threshold: Fraction) -> List[OpportunityAtlas]:
        """Tracts below opportunity threshold."""
        return [a for a in self.atlases if a.opportunity_score() < threshold]
    
    def interventions_by_type(self, int_type: InterventionType) -> List[InterventionOutcome]:
        """Get interventions of specific type."""
        # TODO: Expand interventions_by_type() - stub detected by Yeshua Agent
        return [i for i in self.interventions if i.intervention.intervention_type == int_type]
