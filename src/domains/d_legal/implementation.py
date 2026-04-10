"""D_LEGAL implementation — Legal System, Courts, Access to Justice

Layer: 3 (Judicial)
CardinalStrength: PREDICATIVE
Source: Federal Rules, ABA Standards, Speedy Trial Act
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum, auto
from fractions import Fraction


class CaseType(Enum):
    """Types of legal cases."""
    CIVIL = auto()
    CRIMINAL = auto()
    ADMINISTRATIVE = auto()
    APPELLATE = auto()


class CaseStatus(Enum):
    """Case status."""
    FILED = auto()
    PENDING = auto()
    DISCOVERY = auto()
    TRIAL = auto()
    SETTLED = auto()
    JUDGMENT = auto()
    APPEAL = auto()
    CLOSED = auto()


@dataclass
class CourtCase:
    """Legal case in court system."""
    case_id: str
    case_type: CaseType
    court_id: str
    
    # Parties
    plaintiff_count: int
    defendant_count: int
    pro_se_parties: int  # Self-represented
    
    # Timeline
    date_filed: str
    date_closed: Optional[str]
    trial_date: Optional[str]
    
    # Workload
    motions_filed: int
    hearings_held: int
    discovery_disputes: int
    
    # Outcome
    status: CaseStatus
    judgment_amount: Optional[Fraction]
    appeal_filed: bool
    
    def get_days_pending(self, current_date: str) -> int:
        """Calculate days case has been pending (simplified)."""
        if self.date_closed:
            return 0
        # Would calculate actual date difference
        return 180  # Placeholder


@dataclass
class Court:
    """Court system metrics."""
    court_id: str
    court_name: str
    jurisdiction: str
    
    # Caseload
    cases_pending: int
    cases_resolved_annual: int
    cases_filed_annual: int
    
    # Resources
    judges_active: int
    support_staff: int
    
    # Timeliness
    cases_over_12_months: int
    cases_over_24_months: int
    
    # Access
    e_filing_available: bool
    interpreter_services: bool
    self_help_center: bool
    
    def get_clearance_rate(self) -> Fraction:
        """Calculate clearance rate (resolved/filed)."""
        if self.cases_filed_annual == 0:
            return Fraction(1)
        return Fraction(self.cases_resolved_annual, self.cases_filed_annual)
    
    def get_backlog_ratio(self) -> Fraction:
        """Calculate backlog ratio."""
        if self.cases_resolved_annual == 0:
            return Fraction(0)
        return Fraction(self.cases_pending, self.cases_resolved_annual)


# Legal standards
SPEEDY_TRIAL_DAYS_CRIMINAL = Fraction(70)  # 70 days
CIVIL_CASE_TARGET_MONTHS = Fraction(12)  # 12 months
MIN_CLEARANCE_RATE = Fraction(95, 100)  # 95%


def speedy_trial_limit() -> Fraction:
    """Speedy Trial Act limit for criminal cases."""
    return SPEEDY_TRIAL_DAYS_CRIMINAL


def civil_case_target() -> Fraction:
    """Target resolution time for civil cases."""
    return CIVIL_CASE_TARGET_MONTHS
