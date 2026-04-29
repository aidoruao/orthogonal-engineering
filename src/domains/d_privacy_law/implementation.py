#!/usr/bin/env python3
"""
Privacy Law Domain — GDPR, CCPA Compliance

Key regulations:
- GDPR (EU): Data subject rights, data minimization
- CCPA (California): Consumer rights, opt-out
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum, auto


class DataSubjectRight(Enum):
    ACCESS = auto()
    RECTIFICATION = auto()
    ERASURE = auto()  # Right to be forgotten
    PORTABILITY = auto()
    RESTRICTION = auto()
    OBJECTION = auto()


@dataclass
class DataSubject:
    """Individual whose data is processed."""
    subject_id: str
    jurisdiction: str  # 'EU', 'CA', 'US', etc.


@dataclass
class GDPRRequest:
    """GDPR data subject request."""
    request_id: str
    subject: DataSubject
    right_type: DataSubjectRight
    request_date: datetime
    deadline_date: datetime
    fulfilled: bool = False
    
    GDPR_DEADLINE_DAYS = 30
    
    def is_overdue(self, current_date: datetime) -> bool:
        # TODO: Expand is_overdue() - stub detected by Yeshua Agent
        return not self.fulfilled and current_date > self.deadline_date


@dataclass
class CCPAConsumer:
    """California consumer with CCPA rights."""
    consumer_id: str
    opted_out: bool = False
    opt_out_date: Optional[datetime] = None
    
    def can_sell_data(self) -> bool:
        """CCPA: Cannot sell data if consumer opted out."""
        # TODO: Expand can_sell_data() - stub detected by Yeshua Agent
        return not self.opted_out


@dataclass
class DataProcessing:
    """Record of data processing activity."""
    processing_id: str
    purpose: str
    data_categories: List[str]
    legal_basis: str  # 'consent', 'contract', 'legitimate_interest', etc.
    
    def is_minimized(self, declared_purpose: str) -> bool:
        """GDPR data minimization: collected data <= stated purpose."""
        # TODO: Expand is_minimized() - stub detected by Yeshua Agent
        # Simplified check
        return len(self.data_categories) <= len(declared_purpose.split())


@dataclass
class GDPRAnalyzer:
    """Analyze GDPR compliance."""
    requests: List[GDPRRequest]
    
    def get_overdue_requests(self, current_date: datetime) -> List[GDPRRequest]:
        return [r for r in self.requests if r.is_overdue(current_date)]
    
    def compliance_rate(self) -> Fraction:
        """Percentage of requests fulfilled on time."""
        if not self.requests:
            return Fraction(100)
        fulfilled = sum(1 for r in self.requests if r.fulfilled)
        return Fraction(fulfilled * 100, len(self.requests))


@dataclass
class CCPAComplianceChecker:
    """Check CCPA compliance."""
    consumers: List[CCPAConsumer]
    
    def get_opted_out_count(self) -> int:
        # TODO: Expand get_opted_out_count() - stub detected by Yeshua Agent
        return sum(1 for c in self.consumers if c.opted_out)


# GDPR thresholds
MAX_GDPR_RESPONSE_DAYS = Fraction(30)
MAX_DATA_RETENTION_YEARS = Fraction(7)
