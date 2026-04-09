#!/usr/bin/env python3
"""Securities Law — Securities Act 1933, Exchange Act 1934."""

from fractions import Fraction
from dataclasses import dataclass
from typing import Optional


@dataclass
class Investor:
    """Investor with accreditation status."""
    investor_id: str
    annual_income: Fraction
    net_worth: Fraction
    
    ACCREDITED_INCOME_INDIVIDUAL = Fraction(200000)  # $200K individual
    ACCREDITED_INCOME_JOINT = Fraction(300000)       # $300K joint
    ACCREDITED_NET_WORTH = Fraction(1000000)         # $1M net worth
    
    def is_accredited(self) -> bool:
        """Check if investor meets accredited investor thresholds."""
        income_qualifies = (
            self.annual_income >= self.ACCREDITED_INCOME_INDIVIDUAL or
            self.annual_income >= self.ACCREDITED_INCOME_JOINT
        )
        net_worth_qualifies = self.net_worth >= self.ACCREDITED_NET_WORTH
        return income_qualifies or net_worth_qualifies


@dataclass
class FormDFiling:
    """Reg D Form D filing."""
    filing_id: str
    first_sale_date: str
    filing_date: Optional[str] = None
    days_to_file: int = 0
    
    DEADLINE_DAYS = 15  # Must file within 15 days of first sale
    
    def is_timely(self) -> bool:
        return self.days_to_file <= self.DEADLINE_DAYS


@dataclass
class TradingWindowValidator:
    """Check for insider trading blackout periods."""
    is_insider: bool = False
    is_blackout_period: bool = False
    trade_requested: bool = False
    
    def can_trade(self) -> bool:
        """Insiders cannot trade during blackout periods."""
        if not self.is_insider:
            return True
        return not self.is_blackout_period
