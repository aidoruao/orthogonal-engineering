#!/usr/bin/env python3
"""Immigration Law — INA, visa categories, processing times."""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum, auto


class VisaCategory(Enum):
    EB1 = 1  # Priority workers
    EB2 = 2  # Advanced degree
    EB3 = 3  # Skilled workers
    EB4 = 4  # Special immigrants
    EB5 = 5  # Investors
    F1 = 11  # Family sponsored


@dataclass
class VisaApplicant:
    """Immigration visa applicant."""
    applicant_id: str
    priority_date: str
    visa_category: VisaCategory
    country_of_chargeability: str
    
    def preference_priority(self) -> int:
        """Lower number = higher priority."""
        return self.visa_category.value


@dataclass
class VisaCategoryChecker:
    """Check visa category eligibility."""
    applicant: VisaApplicant
    required_education_years: int = 0
    actual_education_years: int = 0
    investment_amount: Fraction = Fraction(0)
    
    EB5_MIN_INVESTMENT = Fraction(1050000)  # $1.05M (or $800K in TEA)
    
    def meets_category_requirements(self) -> bool:
        cat = self.applicant.visa_category
        if cat == VisaCategory.EB1:
            return True  # Assumed extraordinary ability
        if cat == VisaCategory.EB2:
            return self.actual_education_years >= self.required_education_years
        if cat == VisaCategory.EB5:
            return self.investment_amount >= self.EB5_MIN_INVESTMENT
        return True


@dataclass
class ProcessingTimer:
    """Track visa processing against statutory deadlines."""
    application_date: str
    current_date: str
    days_elapsed: int
    statutory_deadline_days: int = 180
    
    def is_overdue(self) -> bool:
        return self.days_elapsed > self.statutory_deadline_days


@dataclass
class StatusStateMachine:
    """Track valid immigration status transitions."""
    current_status: str
    requested_status: str
    
    VALID_TRANSITIONS = {
        "F1": ["OPT", "H1B"],
        "OPT": ["H1B"],
        "H1B": ["PERM", "I140", "I485"],
        "I485": ["LPR"],
    }
    
    def is_valid_transition(self) -> bool:
        valid_next = self.VALID_TRANSITIONS.get(self.current_status, [])
        return self.requested_status in valid_next
