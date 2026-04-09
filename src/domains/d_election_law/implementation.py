#!/usr/bin/env python3
"""
Election Law Domain — Voter Eligibility, Chain of Custody, Recounts

Key concepts:
- One person, one vote
- Ballot chain of custody
- Recount thresholds
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum, auto


class BallotStatus(Enum):
    CAST = auto()
    RECEIVED = auto()
    COUNTED = auto()
    CHALLENGED = auto()
    REJECTED = auto()


@dataclass
class Voter:
    """Registered voter."""
    voter_id: str
    registered: bool = False
    voted: bool = False
    vote_timestamp: Optional[datetime] = None


@dataclass
class EligibilityVerifier:
    """Verify voter eligibility."""
    voter: Voter
    
    def is_eligible(self) -> bool:
        """One person, one vote: registered and not yet voted."""
        return self.voter.registered and not self.voter.voted


@dataclass
class BallotCustodyRecord:
    """Single link in chain of custody."""
    timestamp: datetime
    location: str
    custodian: str
    ballot_count: int
    seal_number: str


@dataclass
class BallotCustodyTracker:
    """Track ballot chain of custody."""
    ballot_batch_id: str
    custody_chain: List[BallotCustodyRecord]
    
    def chain_unbroken(self) -> bool:
        """Chain of custody must be unbroken."""
        if len(self.custody_chain) < 2:
            return True
        
        # Check timestamps are sequential
        for i in range(1, len(self.custody_chain)):
            if self.custody_chain[i].timestamp < self.custody_chain[i-1].timestamp:
                return False
        
        return True
    
    def ballot_count_consistent(self) -> bool:
        """Ballot count must remain consistent throughout chain."""
        if not self.custody_chain:
            return True
        
        first_count = self.custody_chain[0].ballot_count
        return all(r.ballot_count == first_count for r in self.custody_chain)


@dataclass
class ElectionResult:
    """Election vote totals."""
    candidate: str
    votes: int


@dataclass
class RecountAnalyzer:
    """Analyze if recount is required."""
    results: List[ElectionResult]
    total_votes_cast: int
    
    RECOUNT_THRESHOLD_PCT = Fraction(1, 2)  # 0.5% margin triggers recount
    
    def winning_margin(self) -> Fraction:
        """Calculate margin between top two candidates."""
        if len(self.results) < 2:
            return Fraction(0)
        
        sorted_results = sorted(self.results, key=lambda r: r.votes, reverse=True)
        winner_votes = sorted_results[0].votes
        runner_up_votes = sorted_results[1].votes
        
        if self.total_votes_cast == 0:
            return Fraction(0)
        
        return Fraction(abs(winner_votes - runner_up_votes), self.total_votes_cast)
    
    def recount_required(self) -> bool:
        """Check if margin is within recount threshold."""
        margin_pct = self.winning_margin() * Fraction(100)
        return margin_pct < self.RECOUNT_THRESHOLD_PCT


# Election thresholds
MIN_TURNOUT_PCT = Fraction(50)  # Some jurisdictions require minimum turnout
MAX_SPOILED_PCT = Fraction(2)  # Maximum acceptable spoiled ballot rate
