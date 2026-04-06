"""D_HABEAS_CORPUS implementation — Habeas Corpus

Implements Article I, Section 9: Suspension of habeas corpus only in cases
of rebellion or invasion. Ensures no detention without judicial review.

Layer: 1 (Constitutional)
CardinalStrength: INACCESSIBLE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class SuspensionStatus(Enum):
    """Status of habeas corpus suspension."""
    NOT_SUSPENDED = auto()
    SUSPENDED_REBELLION = auto()     # Article I valid suspension
    SUSPENDED_INVASION = auto()      # Article I valid suspension
    SUSPENDED_INVALID = auto()       # Unconstitutional suspension


class DetentionType(Enum):
    """Types of detention."""
    CRIMINAL = auto()
    IMMIGRATION = auto()
    NATIONAL_SECURITY = auto()
    MILITARY = auto()
    MENTAL_HEALTH = auto()


class HabeasStatus(Enum):
    """Status of habeas corpus petition."""
    PENDING = auto()
    GRANTED = auto()
    DENIED = auto()
    DISMISSED = auto()


@dataclass
class DetentionCase:
    """A case of detention subject to habeas corpus review."""
    case_id: str
    detainee_name: str
    detention_type: DetentionType
    detention_start: datetime
    detention_location: str
    
    # Legal basis
    criminal_charges: Optional[str] = None
    bail_set: Optional[Fraction] = None
    bail_paid: bool = False
    
    # Review status
    judicial_review_completed: bool = False
    review_date: Optional[datetime] = None
    
    def is_lawful_detention(self) -> bool:
        """
        Check if detention is lawful under habeas corpus.
        
        Requires:
        - Criminal charges filed, OR
        - Lawful immigration hold, OR
        - Valid national security detention authority
        """
        if self.detention_type == DetentionType.CRIMINAL:
            return self.criminal_charges is not None
        
        # All other detention types require judicial review
        return self.judicial_review_completed
    
    def days_detained(self) -> int:
        """Calculate days in detention."""
        delta = datetime.now() - self.detention_start
        return delta.days


@dataclass
class HabeasPetition:
    """A petition for writ of habeas corpus."""
    petition_id: str
    case_id: str
    petitioner_name: str
    filing_date: datetime
    grounds: str  # Legal grounds for petition
    
    status: HabeasStatus = HabeasStatus.PENDING
    hearing_date: Optional[datetime] = None
    court_decision: str = ""
    
    def is_timely(self) -> bool:
        """Check if petition is timely filed."""
        # Habeas petitions generally have no statute of limitations
        # for challenging detention
        return True


class HabeasCorpusChecker:
    """Habeas corpus compliance checker (Article I, Section 9)."""
    
    def __init__(self):
        self.detention_cases: Dict[str, DetentionCase] = {}
        self.petitions: Dict[str, HabeasPetition] = {}
        self.suspension_status: SuspensionStatus = SuspensionStatus.NOT_SUSPENDED
        self.suspension_reason: str = ""
        self.suspension_date: Optional[datetime] = None
    
    def register_detention(
        self,
        case_id: str,
        detainee_name: str,
        detention_type: DetentionType,
        detention_location: str,
        criminal_charges: Optional[str] = None,
    ) -> DetentionCase:
        """Register a new detention case."""
        case = DetentionCase(
            case_id=case_id,
            detainee_name=detainee_name,
            detention_type=detention_type,
            detention_start=datetime.now(),
            detention_location=detention_location,
            criminal_charges=criminal_charges,
        )
        self.detention_cases[case_id] = case
        return case
    
    def suspend_habeas_corpus(
        self,
        reason: str,
        is_rebellion: bool = False,
        is_invasion: bool = False,
    ) -> Dict:
        """
        Attempt to suspend habeas corpus.
        
        Article I, Section 9: Suspension only allowed in cases of
        rebellion or invasion.
        """
        if not is_rebellion and not is_invasion:
            self.suspension_status = SuspensionStatus.SUSPENDED_INVALID
            return {
                "suspended": False,
                "valid": False,
                "reason": "Suspension requires rebellion or invasion per Article I",
            }
        
        if is_rebellion:
            self.suspension_status = SuspensionStatus.SUSPENDED_REBELLION
        elif is_invasion:
            self.suspension_status = SuspensionStatus.SUSPENDED_INVASION
        
        self.suspension_reason = reason
        self.suspension_date = datetime.now()
        
        return {
            "suspended": True,
            "valid": True,
            "reason": reason,
            "basis": "rebellion" if is_rebellion else "invasion",
        }
    
    def file_habeas_petition(
        self,
        petition_id: str,
        case_id: str,
        petitioner_name: str,
        grounds: str,
    ) -> HabeasPetition:
        """
        File a petition for writ of habeas corpus.
        
        The Great Writ ensures no detention without judicial review.
        """
        # Check if habeas is suspended
        if self.suspension_status != SuspensionStatus.NOT_SUSPENDED:
            # Even during suspension, some review may be available
            pass
        
        petition = HabeasPetition(
            petition_id=petition_id,
            case_id=case_id,
            petitioner_name=petitioner_name,
            filing_date=datetime.now(),
            grounds=grounds,
        )
        self.petitions[petition_id] = petition
        return petition
    
    def conduct_judicial_review(
        self,
        case_id: str,
        lawful_detention: bool,
    ) -> Dict:
        """
        Conduct judicial review of detention.
        
        Core habeas corpus function: court reviews lawfulness of detention.
        """
        if case_id not in self.detention_cases:
            return {"reviewed": False, "reason": "Case not found"}
        
        case = self.detention_cases[case_id]
        case.judicial_review_completed = True
        case.review_date = datetime.now()
        
        return {
            "reviewed": True,
            "case_id": case_id,
            "lawful": lawful_detention,
            "detainee": case.detainee_name,
        }
    
    def can_challenge_detention(self, case_id: str) -> bool:
        """
        Check if detention can be challenged via habeas corpus.
        
        Generally always available unless validly suspended.
        """
        if case_id not in self.detention_cases:
            return False
        
        # If habeas is suspended, challenge may be limited
        if self.suspension_status == SuspensionStatus.SUSPENDED_INVALID:
            # Invalid suspension - habeas still available
            return True
        elif self.suspension_status in [
            SuspensionStatus.SUSPENDED_REBELLION,
            SuspensionStatus.SUSPENDED_INVASION,
        ]:
            # Valid suspension - challenge may be limited
            return False
        
        return True
    
    def get_detention_summary(self) -> dict:
        """Get summary of detention cases and habeas petitions."""
        total = len(self.detention_cases)
        reviewed = sum(1 for c in self.detention_cases.values() if c.judicial_review_completed)
        pending_habeas = sum(
            1 for p in self.petitions.values() 
            if p.status == HabeasStatus.PENDING
        )
        
        return {
            "total_detentions": total,
            "judicially_reviewed": reviewed,
            "pending_review": total - reviewed,
            "habeas_petitions_filed": len(self.petitions),
            "habeas_pending": pending_habeas,
            "suspension_status": self.suspension_status.name,
        }


def check_habeas_corpus_available(
    is_rebellion: bool = False,
    is_invasion: bool = False,
) -> bool:
    """
    Convenience function to check if habeas corpus is available.
    
    Returns True unless validly suspended (rebellion or invasion).
    """
    if is_rebellion or is_invasion:
        return False
    return True
