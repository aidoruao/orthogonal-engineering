"""D_DIGITAL_GOVERNANCE implementation — Digital Governance & Platform Regulation

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Regulatory Standards:
- EU Digital Services Act (DSA) 2022/2065
- EU Digital Markets Act (DMA) 2022/1925
- GDPR 2016/679
- UK Online Safety Bill
- Germany NetzDG
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class PlatformCategory(Enum):
    """DSA platform categories by scale/risk."""
    VERY_LARGE = auto()      # >45M EU users (Article 33)
    LARGE = auto()           # >10M EU users
    MEDIUM = auto()          # >1M EU users
    SMALL = auto()           # <1M EU users


class ContentCategory(Enum):
    """Content categories under DSA Article 13."""
    ILLEGAL = auto()         # Illegal content (all platforms)
    HARMFUL = auto()         # Harmful but legal (VLOPs)
    PROTECTED = auto()       # Protected speech
    MINORITY = auto()        # Minority linguistic content


class SystemicRiskLevel(Enum):
    """Systemic risk levels under DSA Article 34."""
    CRITICAL = auto()        # Severe societal impact
    HIGH = auto()            # Significant societal impact
    MODERATE = auto()        # Some societal impact
    LOW = auto()             # Minimal societal impact


@dataclass(frozen=True)
class UserMetrics:
    """Monthly active user metrics per DSA Article 33."""
    eu_monthly_active: int
    global_monthly_active: int
    last_reported: datetime
    
    def eu_percentage(self) -> Fraction:
        """Fraction of users in EU (for DSA jurisdiction)."""
        if self.global_monthly_active == 0:
            return Fraction(0)
        return Fraction(self.eu_monthly_active, self.global_monthly_active)


@dataclass
class ContentModerationDecision:
    """A content moderation action with DSA Article 17 requirements."""
    decision_id: str
    content_id: str
    content_category: ContentCategory
    action_taken: str  # removal, restriction, demonetization
    timestamp: datetime
    automated: bool
    human_reviewed: bool
    statement_of_reasons: Optional[str] = None
    appeal_window_days: int = 6  # DSA requires 6-month appeal window
    
    def has_required_statement(self) -> bool:
        """DSA Article 17 requires statement of reasons for restrictions."""
        if self.content_category == ContentCategory.PROTECTED:
            return self.statement_of_reasons is not None and len(self.statement_of_reasons) >= 50
        return True


@dataclass
class TransparencyReport:
    """DSA Article 15 transparency reporting data."""
    reporting_period: str  # YYYY-MM
    content_removed_count: int
    content_restricted_count: int
    accounts_suspended: int
    appeals_received: int
    appeals_upheld: int
    avg_response_time_hours: Fraction
    
    def appeal_upheld_rate(self) -> Fraction:
        """Fraction of appeals that were successful."""
        if self.appeals_received == 0:
            return Fraction(0)
        return Fraction(self.appeals_upheld, self.appeals_received)


@dataclass
class RiskAssessment:
    """DSA Article 34 systemic risk assessment."""
    assessment_date: datetime
    risk_level: SystemicRiskLevel
    mitigation_measures: List[str]
    independent_audit: bool
    audit_date: Optional[datetime] = None
    
    def is_current(self) -> bool:
        """Assessments must be annual for VLOPs."""
        if self.assessment_date is None:
            return False
        age_days = (datetime.now() - self.assessment_date).days
        return age_days <= 365


@dataclass
class Platform:
    """Digital platform subject to DSA/DMA regulation."""
    platform_id: str
    name: str
    category: PlatformCategory
    user_metrics: UserMetrics
    content_decisions: List[ContentModerationDecision] = field(default_factory=list)
    transparency_reports: List[TransparencyReport] = field(default_factory=list)
    risk_assessments: List[RiskAssessment] = field(default_factory=list)
    
    def is_vlop(self) -> bool:
        """Very Large Online Platform: >45M EU users (DSA Article 33)."""
        return self.user_metrics.eu_monthly_active >= 45_000_000
    
    def latest_risk_assessment(self) -> Optional[RiskAssessment]:
        """Most recent systemic risk assessment."""
        if not self.risk_assessments:
            return None
        return max(self.risk_assessments, key=lambda x: x.assessment_date)
    
    def decisions_requiring_statement(self) -> List[ContentModerationDecision]:
        """All decisions lacking required statements of reasons."""
        return [d for d in self.content_decisions if not d.has_required_statement()]
    
    def latest_transparency_report(self) -> Optional[TransparencyReport]:
        """Most recent transparency report."""
        if not self.transparency_reports:
            return None
        return max(self.transparency_reports, key=lambda x: x.reporting_period)


@dataclass
class DigitalGovernanceChecker:
    """Checker for digital governance compliance."""
    platforms: List[Platform] = field(default_factory=list)
    
    def get_vlops(self) -> List[Platform]:
        """Return all Very Large Online Platforms."""
        return [p for p in self.platforms if p.is_vlop()]
    
    def platforms_without_current_risk_assessment(self) -> List[Platform]:
        """VLOPs requiring annual risk assessment per DSA Article 34."""
        result = []
        for p in self.get_vlops():
            latest = p.latest_risk_assessment()
            if latest is None or not latest.is_current():
                result.append(p)
        return result
    
    def decisions_without_statements(self) -> List[ContentModerationDecision]:
        """All content decisions missing required statements of reasons."""
        result = []
        for p in self.platforms:
            result.extend(p.decisions_requiring_statement())
        return result
    
    def platforms_without_transparency_report(self, year_month: str) -> List[Platform]:
        """Platforms missing required transparency reports."""
        result = []
        for p in self.platforms:
            has_report = any(r.reporting_period == year_month for r in p.transparency_reports)
            if not has_report:
                result.append(p)
        return result
