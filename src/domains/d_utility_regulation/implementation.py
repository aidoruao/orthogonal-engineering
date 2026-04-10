"""D_UTILITY_REGULATION implementation — Utility Regulation, Rate Setting, Reliability

Layer: 3 (Economic Regulation)
CardinalStrength: PREDICATIVE
Source: FERC, State PUCs, NERC standards
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum, auto
from fractions import Fraction


class UtilityType(Enum):
    """Types of regulated utilities."""
    ELECTRIC = auto()
    GAS = auto()
    WATER = auto()
    TELECOM = auto()


class RateCaseStatus(Enum):
    """Rate case status."""
    PENDING = auto()
    APPROVED = auto()
    DENIED = auto()
    MODIFIED = auto()


@dataclass
class UtilityCompany:
    """Regulated utility company."""
    company_id: str
    name: str
    utility_type: UtilityType
    
    # Service territory
    customers_total: int
    customers_residential: int
    customers_commercial: int
    customers_industrial: int
    
    # Reliability (electric)
    saidi_minutes: Fraction  # System Average Interruption Duration
    saifi_frequency: Fraction  # System Average Interruption Frequency
    
    # Rate case
    rate_case_pending: bool
    requested_rate_increase: Fraction  # Percentage
    approved_rate_increase: Optional[Fraction]
    
    # Financial
    revenue_annual: Fraction
    operating_costs: Fraction
    capital_investment: Fraction
    
    def get_return_on_revenue(self) -> Fraction:
        """Calculate return on revenue."""
        if self.revenue_annual == 0:
            return Fraction(0)
        return (self.revenue_annual - self.operating_costs) / self.revenue_annual
    
    def get_reliability_score(self) -> Fraction:
        """Calculate reliability score (lower SAIDI = higher score)."""
        if self.utility_type != UtilityType.ELECTRIC:
            return Fraction(1)
        # Score decreases as SAIDI increases
        if self.saidi_minutes > 240:
            return Fraction(0)
        return Fraction(1) - (self.saidi_minutes / 240)


@dataclass
class RateCase:
    """Utility rate case proceeding."""
    case_id: str
    company_id: str
    status: RateCaseStatus
    
    # Rate request
    current_revenue: Fraction
    requested_revenue: Fraction
    test_year: str
    
    # Cost of service
    rate_base: Fraction
    allowed_return_rate: Fraction
    operating_expenses: Fraction
    
    # Public participation
    public_comments: int
    public_hearings: int
    intervenor_participation: bool
    
    def get_return_on_equity(self) -> Fraction:
        """Calculate requested return on equity."""
        profit = self.requested_revenue - self.operating_expenses
        if self.rate_base == 0:
            return Fraction(0)
        return profit / self.rate_base


# Utility standards
MAX_SAIDI_MINUTES = Fraction(240)  # 4 hours annual average
MAX_ACCEPTABLE_ROE = Fraction(11, 100)  # 11%
MIN_RELIABILITY_SCORE = Fraction(7, 10)  # 70%


def max_saidi_limit() -> Fraction:
    """Maximum acceptable SAIDI for electric utilities."""
    return MAX_SAIDI_MINUTES


def max_allowed_roe() -> Fraction:
    """Maximum allowed return on equity."""
    return MAX_ACCEPTABLE_ROE
