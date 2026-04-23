#!/usr/bin/env python3
"""Immigration Law — INA, visa categories, processing times.

INA § 203(b)(1) (8 U.S.C. § 1153(b)(1)); 8 C.F.R. § 204.5;
Matter of Kazarian, 22 I&N Dec. 717 (BIA 1999).
"""

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


@dataclass(frozen=True)
class VisaApplicant:
    """Immigration visa applicant."""
    applicant_id: str
    priority_date: str
    visa_category: VisaCategory
    country_of_chargeability: str
    education_years: int = 0
    investment_amount: Fraction = Fraction(0)

    def preference_priority(self) -> int:
        """Lower number = higher priority."""
        return self.visa_category.value


@dataclass(frozen=True)
class VisaCategoryChecker:
    """Check visa category eligibility."""
    applicant: VisaApplicant
    required_education_years: int = 0
    EB5_MIN_INVESTMENT: Fraction = Fraction(1050000)

    def qualification_score(self) -> Fraction:
        """Fraction score of qualification (Matter of Kazarian)."""
        cat = self.applicant.visa_category
        if cat == VisaCategory.EB1:
            return Fraction(1, 1)
        if cat == VisaCategory.EB2:
            if self.required_education_years <= 0:
                return Fraction(1, 1)
            return Fraction(
                min(self.applicant.education_years, self.required_education_years),
                self.required_education_years
            )
        if cat == VisaCategory.EB5:
            if self.EB5_MIN_INVESTMENT <= 0:
                return Fraction(1, 1)
            return Fraction(
                min(self.applicant.investment_amount, self.EB5_MIN_INVESTMENT),
                self.EB5_MIN_INVESTMENT
            )
        return Fraction(1, 1)


@dataclass(frozen=True)
class ProcessingTimer:
    """Track visa processing against statutory deadlines."""
    application_date: str
    current_date: str
    days_elapsed: int
    statutory_deadline_days: int = 180

    def processing_ratio(self) -> Fraction:
        """Fraction of statutory deadline consumed (INA § 203)."""
        if self.statutory_deadline_days <= 0:
            return Fraction(0, 1)
        return Fraction(self.days_elapsed, self.statutory_deadline_days)

    def is_overdue(self) -> bool:
        return self.processing_ratio() > Fraction(1, 1)


@dataclass(frozen=True)
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

    def transition_validity_score(self) -> Fraction:
        """1 if valid transition, 0 otherwise."""
        valid_next = self.VALID_TRANSITIONS.get(self.current_status, [])
        if self.requested_status in valid_next:
            return Fraction(1, 1)
        return Fraction(0, 1)
