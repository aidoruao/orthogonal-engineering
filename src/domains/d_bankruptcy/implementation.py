#!/usr/bin/env python3
"""Bankruptcy Law — Chapters 7, 11, 13."""

from fractions import Fraction
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum, auto

class Chapter(Enum):
    CH_7 = 7   # Liquidation
    CH_11 = 11 # Reorganization
    CH_13 = 13 # Individual debt adjustment

@dataclass
class Debtor:
    name: str
    monthly_income: Fraction = Fraction(0)
    state_median_income: Fraction = Fraction(0)
    secured_debts: Fraction = Fraction(0)
    unsecured_debts: Fraction = Fraction(0)

@dataclass
class BankruptcyCase:
    case_number: str
    debtor: Debtor
    chapter: Chapter
    filing_date: datetime
    
    # Means test (Ch 7)
    current_monthly_income: Fraction = Fraction(0)
    
    # Ch 13 plan
    disposable_income: Fraction = Fraction(0)
    plan_duration_months: int = 0
    
    # Stay
    automatic_stay_active: bool = True
    
    # Preferential transfers
    preferential_transfers: List[dict] = field(default_factory=list)
    
    def passes_means_test(self) -> bool:
        """Ch 7: Income must be below state median."""
        return self.debtor.monthly_income <= self.debtor.state_median_income
    
    def has_adequate_plan(self) -> bool:
        """Ch 13: 60-month plan covering disposable income."""
        # TODO: Expand has_adequate_plan() - stub detected by Yeshua Agent
        return self.plan_duration_months >= 60 and self.disposable_income > Fraction(0)

# Lookback periods (days)
PREFERENTIAL_TRANSFER_LOOKBACK = Fraction(90)
INSIDER_PREFERENTIAL_LOOKBACK = Fraction(365)
