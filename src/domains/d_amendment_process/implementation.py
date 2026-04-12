"""D_AMENDMENT_PROCESS implementation — Constitutional Amendment Process

Implements Article V amendment process: 2/3 Congress + 3/4 states.
Enforces indelible clauses that cannot be amended away.

Layer: 1 (Constitutional)
CardinalStrength: INACCESSIBLE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class RatificationStatus(Enum):
    """Status of a constitutional amendment."""
    PROPOSED = auto()
    CONGRESSIONALLY_APPROVED = auto()
    RATIFIED = auto()
    REJECTED = auto()
    EXPIRED = auto()


class IndelibleClause(Enum):
    """Clauses that cannot be amended away (Article V)."""
    EQUAL_STATE_SUFFRAGE_IN_SENATE = auto()
    AMENDMENT_PROCESS_ITSELF = auto()
    
    @classmethod
    def get_protected_text(cls) -> dict:
        """Get the protected text for each indelible clause."""
        return {
            cls.EQUAL_STATE_SUFFRAGE_IN_SENATE: 
                "No State, without its Consent, shall be deprived of its equal Suffrage in the Senate",
            cls.AMENDMENT_PROCESS_ITSELF:
                "The amendment process itself cannot be abolished",
        }


@dataclass
class AmendmentProposal:
    """A proposed constitutional amendment."""
    proposal_id: str
    text: str
    proposed_date: datetime
    congressional_approval_date: Optional[datetime] = None
    ratification_deadline: Optional[datetime] = None
    states_ratified: List[str] = field(default_factory=list)
    states_rejected: List[str] = field(default_factory=list)
    status: RatificationStatus = RatificationStatus.PROPOSED
    
    def get_congressional_support_fraction(self) -> Fraction:
        """Calculate fraction of congressional support (need 2/3)."""
        # Simplified: actual implementation would track House + Senate votes
        return Fraction(0, 1)
    
    def get_state_ratification_fraction(self) -> Fraction:
        """Calculate fraction of states ratified (need 3/4 = 38/50)."""
        total_states = 50
        ratified = len(self.states_ratified)
        return Fraction(ratified, total_states)


class AmendmentProcess:
    """Constitutional amendment process checker (Article V)."""
    
    # Article V requirements
    CONGRESSIONAL_SUPERMAJORITY = Fraction(2, 3)
    STATE_RATIFICATION_THRESHOLD = Fraction(3, 4)
    
    def __init__(self):
        self.proposals: dict[str, AmendmentProposal] = {}
        self.amendment_count: int = 27  # Current number of ratified amendments
    
    def propose_amendment(
        self,
        proposal_id: str,
        text: str,
        congressional_support: Fraction,
    ) -> AmendmentProposal:
        """
        Propose a constitutional amendment.
        
        Requires 2/3 support in both House and Senate.
        """
        if congressional_support < self.CONGRESSIONAL_SUPERMAJORITY:
            raise ValueError(
                f"Amendment requires {self.CONGRESSIONAL_SUPERMAJORITY} congressional support, "
                f"got {congressional_support}"
            )
        
        proposal = AmendmentProposal(
            proposal_id=proposal_id,
            text=text,
            proposed_date=datetime.now(),
            status=RatificationStatus.CONGRESSIONALLY_APPROVED,
        )
        self.proposals[proposal_id] = proposal
        return proposal
    
    def check_indelible_clause(self, amendment_text: str) -> Optional[IndelibleClause]:
        """
        Check if amendment attempts to modify an indelible clause.
        
        Article V specifies that no amendment can deprive a state of
        equal suffrage in the Senate without its consent.
        """
        text_lower = amendment_text.lower()
        
        # Check for equal state suffrage modification
        # Keywords: senate, suffrage, representation, equal
        senate_keywords = ["senate", "suffrage"]
        has_senate_content = any(kw in text_lower for kw in senate_keywords)
        removes_equality = "remove" in text_lower or "eliminate" in text_lower
        
        if has_senate_content and removes_equality:
            if "without consent" not in text_lower and "consent" not in text_lower:
                return IndelibleClause.EQUAL_STATE_SUFFRAGE_IN_SENATE
        
        # Also check for explicit equal suffrage modification
        if "equal suffrage" in text_lower and ("remove" in text_lower or "deprive" in text_lower):
            return IndelibleClause.EQUAL_STATE_SUFFRAGE_IN_SENATE
        
        # Check for amendment process abolition
        process_keywords = ["abolish amendment", "no more amendments", "end article v",
                           "abolish the amendment process"]
        if any(kw in text_lower for kw in process_keywords):
            return IndelibleClause.AMENDMENT_PROCESS_ITSELF
        
        return None
    
    def ratify_by_state(
        self,
        proposal_id: str,
        state_name: str,
    ) -> bool:
        """
        Record state ratification of an amendment.
        
        Returns True if amendment is now fully ratified (38+ states).
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if state_name not in proposal.states_ratified:
            proposal.states_ratified.append(state_name)
        
        # Check if threshold reached
        ratification_fraction = proposal.get_state_ratification_fraction()
        if ratification_fraction >= self.STATE_RATIFICATION_THRESHOLD:
            proposal.status = RatificationStatus.RATIFIED
            self.amendment_count += 1
            return True
        
        return False
    
    def is_amendment_valid(
        self,
        proposal_id: str,
    ) -> dict:
        """
        Check if an amendment proposal is valid.
        
        Returns dict with validity status and any issues.
        """
        if proposal_id not in self.proposals:
            return {
                "valid": False,
                "reason": "Proposal not found",
            }
        
        proposal = self.proposals[proposal_id]
        
        # Check for indelible clause violation
        indelible = self.check_indelible_clause(proposal.text)
        if indelible:
            return {
                "valid": False,
                "reason": f"Violates indelible clause: {indelible.name}",
                "indelible_clause": indelible,
            }
        
        # Check ratification status
        ratification_frac = proposal.get_state_ratification_fraction()
        
        return {
            "valid": True,
            "status": proposal.status.name,
            "ratification_progress": f"{ratification_frac.numerator}/{ratification_frac.denominator}",
            "threshold_met": ratification_frac >= self.STATE_RATIFICATION_THRESHOLD,
        }
    
    def get_amendment_summary(self) -> dict:
        """Get summary of all amendment activity."""
        ratified = sum(
            1 for p in self.proposals.values()
            if p.status == RatificationStatus.RATIFIED
        )
        pending = sum(
            1 for p in self.proposals.values()
            if p.status == RatificationStatus.CONGRESSIONALLY_APPROVED
        )
        
        return {
            "total_proposed": len(self.proposals),
            "ratified": ratified,
            "pending": pending,
            "current_amendment_count": self.amendment_count,
        }


def check_amendment_threshold(
    states_ratified: int,
    total_states: int = 50,
) -> bool:
    """
    Convenience function to check if amendment threshold is met.
    
    Requires 3/4 of states (38/50).
    """
    threshold = Fraction(3, 4)
    actual = Fraction(states_ratified, total_states)
    return actual >= threshold


@dataclass(frozen=True)
class ConstitutionalAmendment:
    """A proposed constitutional amendment under Article V."""
    amendment_id: str
    proposal_method: str  # "congress_two_thirds" or "convention"
    ratification_method: str  # "state_legislatures" or "state_conventions"
    states_ratified: Fraction
    states_required: Fraction
    proposed_by_congress: bool
    ratification_complete: bool
