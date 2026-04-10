"""D_LICENSING implementation — Professional & Occupational Licensing

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- State licensing board regulations
- Interstate compacts (Nurse Licensure Compact, etc.)
- sunset review requirements
- Continuing education (CE/CME/CLE)
- Uniform Licensing Standards (Dept of Labor)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class LicenseStatus(Enum):
    """Status of professional license."""
    ACTIVE = auto()
    INACTIVE = auto()
    SUSPENDED = auto()
    REVOKED = auto()
    EXPIRED = auto()
    PENDING = auto()
    PROBATION = auto()


class LicenseType(Enum):
    """Categories of licensed professions."""
    MEDICAL = auto()
    LEGAL = auto()
    ACCOUNTING = auto()
    ENGINEERING = auto()
    COSMETOLOGY = auto()
    CONTRACTOR = auto()
    REAL_ESTATE = auto()
    TEACHING = auto()
    DRIVING = auto()


@dataclass(frozen=True)
class License:
    """Professional or occupational license."""
    license_number: str
    license_type: LicenseType
    profession: str
    
    holder_name: str
    holder_id: str
    
    issuing_authority: str
    jurisdiction: str  # State/country
    
    # Dates
    issue_date: datetime
    expiration_date: datetime
    status: LicenseStatus
    
    # Compact/multi-state
    compact_member: bool  # Part of interstate compact
    compact_privileges: List[str] = field(default_factory=list)  # Other jurisdictions
    
    def is_active(self) -> bool:
        """License currently valid."""
        return self.status == LicenseStatus.ACTIVE
    
    def is_expired(self) -> bool:
        """Past expiration date."""
        return datetime.now() > self.expiration_date
    
    def days_until_expiration(self) -> int:
        """Days remaining."""
        delta = self.expiration_date - datetime.now()
        return max(0, delta.days)
    
    def valid_in_jurisdiction(self, jurisdiction: str) -> bool:
        """Check if license valid in given jurisdiction."""
        if self.jurisdiction == jurisdiction:
            return self.is_active() and not self.is_expired()
        if self.compact_member and jurisdiction in self.compact_privileges:
            return self.is_active() and not self.is_expired()
        return False


@dataclass
class ContinuingEducation:
    """CE/CME/CLE requirements and completion."""
    license_number: str
    reporting_period_start: datetime
    reporting_period_end: datetime
    
    required_hours: Fraction
    completed_hours: Fraction
    
    # Category breakdown
    ethics_required: Fraction
    ethics_completed: Fraction
    
    def completion_rate(self) -> Fraction:
        """Fraction of required hours completed."""
        if self.required_hours == 0:
            return Fraction(1)
        return self.completed_hours / self.required_hours
    
    def is_complete(self) -> bool:
        """All requirements satisfied."""
        return (
            self.completed_hours >= self.required_hours and
            self.ethics_completed >= self.ethics_required
        )
    
    def hours_remaining(self) -> Fraction:
        """Hours still needed."""
        return max(Fraction(0), self.required_hours - self.completed_hours)


@dataclass
class DisciplinaryAction:
    """License discipline record."""
    action_id: str
    license_number: str
    
    action_type: str  # suspension, revocation, probation, reprimand
    action_date: datetime
    
    # Grounds
    violation_type: str
    violation_description: str
    
    # Outcome
    duration_days: Optional[int]  # For suspensions
    conditions: List[str] = field(default_factory=list)
    
    # Status
    appealed: bool
    appeal_status: Optional[str] = None


@dataclass
class LicensingBoard:
    """Professional licensing authority."""
    board_id: str
    name: str
    jurisdiction: str
    license_type: LicenseType
    
    # Requirements
    education_required: str
    examination_required: str
    experience_hours: int
    
    # Sunset review
    sunset_review_date: Optional[datetime]
    last_sunset_review: Optional[datetime]
    
    # Statistics
    total_licenses: int
    active_licenses: int
    
    def sunset_current(self) -> bool:
        """License requirements reviewed recently."""
        if self.last_sunset_review is None:
            return False
        days = (datetime.now() - self.last_sunset_review).days
        return days <= 365 * 5  # 5 years
    
    def inactive_rate(self) -> Fraction:
        """Fraction of licenses not active."""
        if self.total_licenses == 0:
            return Fraction(0)
        inactive = self.total_licenses - self.active_licenses
        return Fraction(inactive, self.total_licenses)


@dataclass
class ReciprocityAgreement:
    """Interstate or international license reciprocity."""
    agreement_id: str
    from_jurisdiction: str
    to_jurisdiction: str
    profession: str
    
    # Requirements for reciprocity
    years_license_held: int
    no_discipline_required: bool
    additional_exam: bool
    additional_training_hours: int
    
    def qualifies(self, license: License, ce: ContinuingEducation) -> bool:
        """Check if license holder qualifies for reciprocity."""
        if not license.is_active():
            return False
        
        years_held = (datetime.now() - license.issue_date).days / 365
        if years_held < self.years_license_held:
            return False
        
        if self.no_discipline_required:
            # Would check disciplinary history
            pass
        
        return True


@dataclass
class LicensingChecker:
    """Checker for licensing compliance."""
    licenses: List[License] = field(default_factory=list)
    ce_records: List[ContinuingEducation] = field(default_factory=list)
    boards: List[LicensingBoard] = field(default_factory=list)
    disciplinary_actions: List[DisciplinaryAction] = field(default_factory=list)
    
    def expired_licenses(self) -> List[License]:
        """Licenses past expiration."""
        return [l for l in self.licenses if l.is_expired()]
    
    def ce_deficient(self) -> List[ContinuingEducation]:
        """Licensees not meeting education requirements."""
        return [c for c in self.ce_records if not c.is_complete()]
    
    def boards_needing_sunset_review(self) -> List[LicensingBoard]:
        """Boards overdue for sunset review."""
        return [b for b in self.boards if not b.sunset_current()]
    
    def suspended_practicing(self) -> List[DisciplinaryAction]:
        """Disciplined licensees who may still be practicing."""
        recent = []
        for d in self.disciplinary_actions:
            if d.action_type in ("suspension", "revocation"):
                days = (datetime.now() - d.action_date).days
                if days < 365:  # Recent action
                    recent.append(d)
        return recent
