"""D_WHITECOLLAR implementation — White Collar Crime, Fraud, Compliance

Layer: 3 (Criminal/Regulatory)
CardinalStrength: PREDICATIVE
Source: Sarbanes-Oxley, FCPA, Antitrust, SEC regulations
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum, auto
from fractions import Fraction


class ViolationType(Enum):
    """Types of white collar violations."""
    SECURITIES_FRAUD = auto()
    ACCOUNTING_FRAUD = auto()
    BRIBERY = auto()
    ANTITRUST = auto()
    MONEY_LAUNDERING = auto()
    INSIDER_TRADING = auto()


class InvestigationStatus(Enum):
    """Investigation status."""
    PENDING = auto()
    CHARGED = auto()
    SETTLED = auto()
    ACQUITTED = auto()
    CONVICTED = auto()


@dataclass
class WhiteCollarCase:
    """White collar criminal case."""
    case_id: str
    defendant_id: str
    violation_type: ViolationType
    
    # Financial
    alleged_gain: Fraction
    victim_losses: Fraction
    disgorgement_ordered: Fraction
    fines_ordered: Fraction
    
    # Proceedings
    investigation_status: InvestigationStatus
    compliance_monitor_appointed: bool
    monitor_duration_years: Fraction
    
    # Cooperation
    self_reported: bool
    cooperation_level: Fraction  # 0-1 scale
    remediation_completed: bool
    
    def get_total_penalty(self) -> Fraction:
        """Calculate total financial penalty."""
        return self.disgorgement_ordered + self.fines_ordered
    
    def penalty_to_gain_ratio(self) -> Fraction:
        """Calculate penalty as ratio of alleged gain."""
        if self.alleged_gain == 0:
            return Fraction(0)
        return self.get_total_penalty() / self.alleged_gain


@dataclass
class ComplianceProgram:
    """Corporate compliance program."""
    program_id: str
    company_id: str
    
    # Elements (DOJ Evaluation)
    risk_assessment_current: bool
    policies_procedures_documented: bool
    training_provided: bool
    confidential_reporting_available: bool
    investigations_independent: bool
    continuous_improvement: bool
    
    # Metrics
    employees_trained_annual: int
    total_employees: int
    hotline_reports_annual: int
    investigations_completed: int
    
    def get_training_coverage(self) -> Fraction:
        """Calculate training coverage."""
        if self.total_employees == 0:
            return Fraction(0)
        return Fraction(self.employees_trained_annual, self.total_employees)


# White collar standards
MIN_COOPERATION_FOR_REDUCTION = Fraction(5, 10)  # 50%
MIN_TRAINING_COVERAGE = Fraction(9, 10)  # 90%
US_SENTENCING_GUIDELINES_FACTOR = Fraction(3)  # Up to 3x gain


def min_cooperation_threshold() -> Fraction:
    """Minimum cooperation for penalty reduction."""
    # TODO: Expand min_cooperation_threshold() - stub detected by Yeshua Agent
    return MIN_COOPERATION_FOR_REDUCTION


def max_penalty_multiplier() -> Fraction:
    """Maximum penalty as multiple of gain."""
    # TODO: Expand max_penalty_multiplier() - stub detected by Yeshua Agent
    return US_SENTENCING_GUIDELINES_FACTOR
