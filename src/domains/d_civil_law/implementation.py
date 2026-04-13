"""D_CIVIL_LAW implementation — Civil Law / Torts

Implements tort law: duty → breach → causation → damages functorial chain.
Statute of limitations enforced with filing date documentation.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class TortType(Enum):
    """Types of torts."""
    NEGLIGENCE = auto()
    INTENTIONAL = auto()
    STRICT_LIABILITY = auto()


@dataclass
class DutyBreachCausationDamages:
    """
    Functorial chain: Duty → Breach → Causation → Damages.
    
    All elements must be satisfied for tort liability.
    """
    duty_exists: bool = False
    duty_description: str = ""
    
    breach_occurred: bool = False
    breach_description: str = ""
    
    causation_exists: bool = False
    causation_description: str = ""
    
    damages_amount: Fraction = field(default_factory=lambda: Fraction(0))
    damages_description: str = ""
    
    def is_liable(self) -> bool:
        """Check if all elements of tort are satisfied."""
        return (
            self.duty_exists and
            self.breach_occurred and
            self.causation_exists and
            self.damages_amount > 0
        )
    
    def get_chain_status(self) -> dict:
        """Get status of each element in the chain."""
        return {
            "duty": self.duty_exists,
            "breach": self.breach_occurred,
            "causation": self.causation_exists,
            "damages": self.damages_amount > 0,
            "complete_chain": self.is_liable(),
        }


@dataclass
class StatuteOfLimitations:
    """Statute of limitations with documented filing date."""
    tort_type: TortType
    incident_date: datetime
    filing_date: Optional[datetime] = None
    
    # Limitations periods (varies by jurisdiction and tort type)
    LIMITATION_PERIODS = {
        TortType.NEGLIGENCE: 2,      # 2 years
        TortType.INTENTIONAL: 1,     # 1 year
        TortType.STRICT_LIABILITY: 2, # 2 years
    }
    
    def is_timely(self) -> bool:
        """Check if filing is within statute of limitations."""
        if self.filing_date is None:
            return False
        
        limitation_years = self.LIMITATION_PERIODS.get(self.tort_type, 2)
        deadline = self.incident_date + timedelta(days=limitation_years * 365)
        
        return self.filing_date <= deadline
    
    def get_remaining_days(self) -> int:
        """Get days remaining to file."""
        if self.filing_date:
            return 0
        
        limitation_years = self.LIMITATION_PERIODS.get(self.tort_type, 2)
        deadline = self.incident_date + timedelta(days=limitation_years * 365)
        remaining = deadline - datetime.now()
        
        return max(0, remaining.days)


@dataclass
class TortClaim:
    """A tort claim with all required elements."""
    claim_id: str
    plaintiff: str
    defendant: str
    tort_type: TortType
    
    elements: DutyBreachCausationDamages
    statute: StatuteOfLimitations
    
    def is_valid_claim(self) -> bool:
        """Check if claim is valid (elements + timely filing)."""
        return self.elements.is_liable() and self.statute.is_timely()


class CivilLaw:
    """Civil law / torts system with functorial chain."""
    
    def __init__(self):
        self.claims: List[TortClaim] = []
        self.judgments: List[dict] = []
    
    def file_claim(
        self,
        claim_id: str,
        plaintiff: str,
        defendant: str,
        tort_type: TortType,
        incident_date: datetime,
        filing_date: datetime,
        duty_description: str,
        breach_description: str,
        causation_description: str,
        damages_amount: Fraction,
    ) -> TortClaim:
        """
        File a tort claim.
        
        Must establish duty → breach → causation → damages.
        """
        elements = DutyBreachCausationDamages(
            duty_exists=len(duty_description) > 0,
            duty_description=duty_description,
            breach_occurred=len(breach_description) > 0,
            breach_description=breach_description,
            causation_exists=len(causation_description) > 0,
            causation_description=causation_description,
            damages_amount=damages_amount,
        )
        
        statute = StatuteOfLimitations(
            tort_type=tort_type,
            incident_date=incident_date,
            filing_date=filing_date,
        )
        
        claim = TortClaim(
            claim_id=claim_id,
            plaintiff=plaintiff,
            defendant=defendant,
            tort_type=tort_type,
            elements=elements,
            statute=statute,
        )
        
        self.claims.append(claim)
        return claim
    
    def adjudicate_claim(self, claim_id: str) -> dict:
        """
        Adjudicate a tort claim.
        
        Checks all elements and statute of limitations.
        """
        claim = next((c for c in self.claims if c.claim_id == claim_id), None)
        if not claim:
            return {"error": "Claim not found"}
        
        # Check statute of limitations
        if not claim.statute.is_timely():
            return {
                "claim_id": claim_id,
                "verdict": "DISMISSED",
                "reason": "Statute of limitations expired",
                "elements_proven": False,
            }
        
        # Check functorial chain
        if not claim.elements.is_liable():
            chain = claim.elements.get_chain_status()
            missing = [k for k, v in chain.items() if not v and k != "complete_chain"]
            return {
                "claim_id": claim_id,
                "verdict": "DISMISSED",
                "reason": f"Elements not proven: {missing}",
                "elements_proven": False,
            }
        
        # Award damages
        judgment = {
            "claim_id": claim_id,
            "verdict": "LIABLE",
            "damages": claim.elements.damages_amount,
            "elements_proven": True,
        }
        self.judgments.append(judgment)
        return judgment
    
    def get_civil_summary(self) -> dict:
        """Get summary of civil cases."""
        valid = sum(1 for c in self.claims if c.is_valid_claim())
        dismissed = len(self.claims) - valid
        
        return {
            "total_claims": len(self.claims),
            "valid_claims": valid,
            "dismissed": dismissed,
            "judgments_rendered": len(self.judgments),
        }


def check_statute_of_limitations(
    incident_date: datetime,
    filing_date: datetime,
    years_limit: int,
) -> bool:
    """
    Convenience function to check statute of limitations.
    
    Returns True if filing is timely.
    """
    deadline = incident_date + timedelta(days=years_limit * 365)
    return filing_date <= deadline


@dataclass(frozen=True)
class FrozenTortClaim:
    """A tort claim with its four required elements (Restatement Second of Torts)."""
    claim_id: str
    duty_exists: bool
    breach_occurred: bool
    causation_established: bool
    damages_amount: Fraction
    statute_of_limitations_days: Fraction
    days_since_incident: Fraction


@dataclass(frozen=True)
class FrozenContract:
    """A contract with formation elements and Statute of Frauds requirements."""
    contract_id: str
    offer_present: bool
    acceptance_present: bool
    consideration_present: bool
    in_writing: bool
    contract_value: Fraction
    involves_land: bool
