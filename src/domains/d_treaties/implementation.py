"""D_TREATIES implementation — Treaty Obligations

Implements treaty registry with ratification status, supremacy clause
resolver, and withdrawal notice tracking.

Source: Vienna Convention on the Law of Treaties (1969)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class TreatyStatus(Enum):
    """Status of a treaty in domestic law."""
    UNSIGNED = auto()
    SIGNED = auto()
    RATIFIED = auto()
    IN_FORCE = auto()
    WITHDRAWN = auto()
    SUSPENDED = auto()


@dataclass
class RatificationRecord:
    """Record of treaty ratification."""
    treaty_name: str
    signed_date: Optional[datetime]
    ratified_date: Optional[datetime]
    entry_into_force_date: Optional[datetime]
    domestic_law_reference: str
    status: TreatyStatus
    
    @property
    def is_binding(self) -> bool:
        """Check if treaty is currently binding."""
        return self.status == TreatyStatus.IN_FORCE


@dataclass
class WithdrawalNotice:
    """Notice of treaty withdrawal."""
    treaty_name: str
    notice_date: datetime
    effective_date: datetime
    reason: str
    proper_notice_given: bool
    
    def validate_notice_period(self, required_days: int = 365) -> bool:
        """Check if proper notice period was given."""
        delta = self.effective_date - self.notice_date
        return delta.days >= required_days


class TreatyRegistry:
    """
    Registry of treaties and their domestic status.
    
    Tracks:
      - Ratification status
      - Supremacy over conflicting domestic law
      - Withdrawal notices and timelines
    """
    
    def __init__(self):
        self.treaties: Dict[str, RatificationRecord] = {}
        self.withdrawals: List[WithdrawalNotice] = []
        self.conflicts_resolved: List[Dict] = []
    
    def register_treaty(
        self,
        treaty_name: str,
        signed_date: Optional[datetime],
        domestic_law_reference: str,
    ) -> RatificationRecord:
        """Register a newly signed treaty."""
        record = RatificationRecord(
            treaty_name=treaty_name,
            signed_date=signed_date,
            ratified_date=None,
            entry_into_force_date=None,
            domestic_law_reference=domestic_law_reference,
            status=TreatyStatus.SIGNED,
        )
        self.treaties[treaty_name] = record
        return record
    
    def ratify_treaty(
        self,
        treaty_name: str,
        ratified_date: datetime,
        entry_into_force_date: Optional[datetime] = None,
    ) -> Optional[RatificationRecord]:
        """Record ratification of a treaty."""
        if treaty_name not in self.treaties:
            return None
        
        record = self.treaties[treaty_name]
        record.ratified_date = ratified_date
        record.entry_into_force_date = entry_into_force_date or ratified_date
        record.status = TreatyStatus.IN_FORCE
        
        return record
    
    def check_supremacy(
        self,
        treaty_name: str,
        domestic_law_name: str,
        conflict_description: str,
    ) -> Dict:
        """
        Check if treaty provision supersedes domestic law.
        
        Per Vienna Convention Article 27: "A party may not invoke the
        provisions of its internal law as justification for its failure
        to perform a treaty."
        """
        if treaty_name not in self.treaties:
            return {
                "supremacy_applies": False,
                "reason": "Treaty not registered",
            }
        
        treaty = self.treaties[treaty_name]
        
        if not treaty.is_binding:
            return {
                "supremacy_applies": False,
                "reason": f"Treaty status is {treaty.status.name}",
            }
        
        # Treaty is in force — it supersedes conflicting domestic law
        resolution = {
            "supremacy_applies": True,
            "treaty": treaty_name,
            "domestic_law": domestic_law_name,
            "conflict": conflict_description,
            "resolution": "Treaty provision prevails",
            "domestic_law_amendment_required": True,
        }
        
        self.conflicts_resolved.append(resolution)
        return resolution
    
    def initiate_withdrawal(
        self,
        treaty_name: str,
        notice_date: datetime,
        effective_date: datetime,
        reason: str,
    ) -> WithdrawalNotice:
        """
        Initiate treaty withdrawal with notice.
        
        Per Vienna Convention Article 56, withdrawal requires
        reasonable advance notice (typically 12 months).
        """
        notice = WithdrawalNotice(
            treaty_name=treaty_name,
            notice_date=notice_date,
            effective_date=effective_date,
            reason=reason,
            proper_notice_given=False,
        )
        
        notice.proper_notice_given = notice.validate_notice_period()
        self.withdrawals.append(notice)
        
        # Update treaty status if withdrawal is immediate
        if treaty_name in self.treaties and notice.proper_notice_given:
            if effective_date <= datetime.now():
                self.treaties[treaty_name].status = TreatyStatus.WITHDRAWN
        
        return notice
    
    def get_binding_treaties(self) -> List[RatificationRecord]:
        """Get all currently binding treaties."""
        return [t for t in self.treaties.values() if t.is_binding]
    
    def get_summary(self) -> Dict:
        """Get registry summary."""
        return {
            "total_treaties": len(self.treaties),
            "binding": len(self.get_binding_treaties()),
            "withdrawals": len(self.withdrawals),
            "conflicts_resolved": len(self.conflicts_resolved),
        }


def check_treaty_supremacy(
    treaty_name: str,
    domestic_law_name: str,
    registry: Optional[TreatyRegistry] = None,
) -> Dict:
    """
    Convenience function to check treaty supremacy.
    
    Usage:
        result = check_treaty_supremacy(
            treaty_name="Geneva Conventions",
            domestic_law_name="Military Procedures Act",
        )
        if result["supremacy_applies"]:
            print("Domestic law must be amended")
    """
    if registry is None:
        registry = TreatyRegistry()
    
    return registry.check_supremacy(
        treaty_name=treaty_name,
        domestic_law_name=domestic_law_name,
        conflict_description="Automatic conflict check",
    )
