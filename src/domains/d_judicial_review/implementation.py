"""D_JUDICIAL_REVIEW implementation — Judicial Review

Implements Marbury v. Madison judicial review: courts can invalidate
unconstitutional statutes. Ensures review by independent situs.

Layer: 1 (Constitutional)
CardinalStrength: INACCESSIBLE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class ReviewOutcome(Enum):
    """Outcome of constitutional review."""
    UPHELD = auto()
    PARTIALLY_INVALIDATED = auto()
    FULLY_INVALIDATED = auto()
    DISMISSED = auto()
    PENDING = auto()


class ChallengeGround(Enum):
    """Grounds for constitutional challenge."""
    FIRST_AMENDMENT = auto()
    FOURTH_AMENDMENT = auto()
    DUE_PROCESS = auto()
    EQUAL_PROTECTION = auto()
    SEPARATION_OF_POWERS = auto()
    FEDERALISM = auto()


@dataclass
class SitusIndependence:
    """
    Independence of the reviewing court (situs).
    
    Per Marbury and the constitutional structure, review must be by
    an independent judiciary, not the branch that enacted the law.
    """
    court_name: str
    enacting_branch_involved: bool = False
    judicial_independence_score: Fraction = Fraction(1, 1)  # 0 to 1
    
    def is_independent(self) -> bool:
        """Check if situs is sufficiently independent."""
        if self.enacting_branch_involved:
            return False
        return self.judicial_independence_score >= Fraction(1, 1)


@dataclass
class ConstitutionalChallenge:
    """A challenge to the constitutionality of a law."""
    challenge_id: str
    statute_name: str
    enacting_branch: str  # "legislative", "executive", etc.
    grounds: List[ChallengeGround]
    challenge_date: datetime
    situs: Optional[SitusIndependence] = None
    outcome: ReviewOutcome = ReviewOutcome.PENDING
    reasoning: str = ""
    
    def can_be_reviewed(self) -> bool:
        """
        Check if this challenge can proceed to judicial review.
        
        Any statute can be challenged for constitutional compliance.
        """
        return len(self.grounds) > 0
    
    def is_valid_situs(self) -> bool:
        """Check if reviewing situs is independent."""
        if self.situs is None:
            return False
        return self.situs.is_independent()


class JudicialReview:
    """Judicial review of constitutional compliance (Marbury v. Madison)."""
    
    def __init__(self):
        self.challenges: dict[str, ConstitutionalChallenge] = {}
        self.review_history: List[ConstitutionalChallenge] = []
        self.statutes_invalidated: Set[str] = set()
    
    def file_challenge(
        self,
        challenge_id: str,
        statute_name: str,
        enacting_branch: str,
        grounds: List[ChallengeGround],
    ) -> ConstitutionalChallenge:
        """
        File a constitutional challenge against a statute.
        
        Any party with standing can challenge any statute.
        """
        challenge = ConstitutionalChallenge(
            challenge_id=challenge_id,
            statute_name=statute_name,
            enacting_branch=enacting_branch,
            grounds=grounds,
            challenge_date=datetime.now(),
        )
        self.challenges[challenge_id] = challenge
        return challenge
    
    def assign_independent_situs(
        self,
        challenge_id: str,
        court_name: str,
    ) -> bool:
        """
        Assign an independent judicial situs to review the challenge.
        
        The situs must be independent of the enacting branch.
        """
        if challenge_id not in self.challenges:
            return False
        
        challenge = self.challenges[challenge_id]
        
        # Situs is independent if not the enacting branch
        situs = SitusIndependence(
            court_name=court_name,
            enacting_branch_involved=False,
            judicial_independence_score=Fraction(1, 1),
        )
        
        challenge.situs = situs
        return True
    
    def conduct_review(
        self,
        challenge_id: str,
        statute_unconstitutional: bool,
        reasoning: str,
    ) -> ReviewOutcome:
        """
        Conduct judicial review of the challenged statute.
        
        Returns the outcome of the review.
        """
        if challenge_id not in self.challenges:
            return ReviewOutcome.DISMISSED
        
        challenge = self.challenges[challenge_id]
        
        # Must have independent situs
        if not challenge.is_valid_situs():
            challenge.outcome = ReviewOutcome.DISMISSED
            return ReviewOutcome.DISMISSED
        
        # Conduct review
        if statute_unconstitutional:
            challenge.outcome = ReviewOutcome.FULLY_INVALIDATED
            self.statutes_invalidated.add(challenge.statute_name)
        else:
            challenge.outcome = ReviewOutcome.UPHELD
        
        challenge.reasoning = reasoning
        self.review_history.append(challenge)
        return challenge.outcome
    
    def is_statute_valid(self, statute_name: str) -> Optional[bool]:
        """
        Check if a statute has been invalidated by judicial review.
        
        Returns:
            True if upheld, False if invalidated, None if never reviewed.
        """
        if statute_name in self.statutes_invalidated:
            return False
        
        # Check if upheld in any challenge
        for challenge in self.review_history:
            if challenge.statute_name == statute_name:
                if challenge.outcome == ReviewOutcome.UPHELD:
                    return True
        
        return None
    
    def get_review_statistics(self) -> dict:
        """Get statistics on judicial review activity."""
        total = len(self.review_history)
        upheld = sum(1 for c in self.review_history if c.outcome == ReviewOutcome.UPHELD)
        invalidated = len(self.statutes_invalidated)
        
        return {
            "total_challenges_filed": len(self.challenges),
            "reviews_completed": total,
            "statutes_upheld": upheld,
            "statutes_invalidated": invalidated,
            "pending": len(self.challenges) - total,
        }


def check_judicial_review_available(
    statute_name: str,
    enacting_branch: str,
) -> bool:
    """
    Convenience function to check if judicial review is available.
    
    Any statute from any branch can be challenged for constitutional compliance.
    """
    # All statutes are reviewable
    return True
