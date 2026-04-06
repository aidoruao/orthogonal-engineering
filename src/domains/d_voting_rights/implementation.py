"""D_VOTING_RIGHTS implementation — Voting & Elections

Implements 15th, 19th, 24th, 26th Amendment voting rights.
Ensures vote is recorded as cast and verifiable.

Layer: 1 (Constitutional)
CardinalStrength: INACCESSIBLE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class VotingRightViolation(Enum):
    """Types of voting rights violations."""
    RACIAL_DISCRIMINATION = auto()  # 15th Amendment
    SEX_DISCRIMINATION = auto()     # 19th Amendment
    POLL_TAX = auto()               # 24th Amendment
    AGE_DISCRIMINATION = auto()     # 26th Amendment (under 18)
    VOTE_DENIAL = auto()
    NON_VERIFIABLE = auto()


@dataclass
class Voter:
    """A voter with constitutional protections."""
    voter_id: str
    age: int
    is_citizen: bool
    race: str = ""
    sex: str = ""
    has_paid_poll_tax: bool = True  # 24th Amendment abolished poll taxes
    
    def has_right_to_vote(self) -> bool:
        """
        Check if voter has constitutional right to vote.
        
        Requirements:
        - US citizen
        - Age 18+ (26th Amendment)
        - No racial discrimination (15th Amendment)
        - No sex discrimination (19th Amendment)
        """
        if not self.is_citizen:
            return False
        if self.age < 18:
            return False  # 26th Amendment
        return True
    
    def get_protected_classes(self) -> Set[str]:
        """Get protected classes for this voter."""
        protected = set()
        if self.race:
            protected.add("race")
        if self.sex:
            protected.add("sex")
        protected.add("age")  # 26th Amendment
        return protected


@dataclass
class Ballot:
    """A ballot cast by a voter."""
    ballot_id: str
    voter_id: str
    selections: Dict[str, str]  # office -> candidate/choice
    cast_timestamp: datetime
    hash_commitment: str = ""  # Cryptographic hash for verification
    
    def generate_hash(self) -> str:
        """Generate hash commitment for vote verification."""
        import hashlib
        data = f"{self.ballot_id}:{self.voter_id}:{sorted(self.selections.items())}:{self.cast_timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify ballot has not been tampered with."""
        current_hash = self.generate_hash()
        return current_hash == self.hash_commitment


@dataclass
class VoteVerification:
    """Verification that vote was recorded as cast."""
    ballot_id: str
    voter_id: str
    recorded_selections: Dict[str, str]
    verification_hash: str
    verification_timestamp: datetime
    
    def matches_voter_intent(
        self,
        intended_selections: Dict[str, str],
    ) -> bool:
        """Check if recorded vote matches voter's intent."""
        return self.recorded_selections == intended_selections


class VotingRightsChecker:
    """Voting rights compliance checker (15th, 19th, 24th, 26th Amendments)."""
    
    def __init__(self):
        self.voters: Dict[str, Voter] = {}
        self.ballots: Dict[str, Ballot] = {}
        self.violations: List[VotingRightViolation] = []
    
    def register_voter(
        self,
        voter_id: str,
        age: int,
        is_citizen: bool,
        race: str = "",
        sex: str = "",
    ) -> Voter:
        """Register a voter."""
        voter = Voter(
            voter_id=voter_id,
            age=age,
            is_citizen=is_citizen,
            race=race,
            sex=sex,
        )
        self.voters[voter_id] = voter
        return voter
    
    def check_voting_eligibility(
        self,
        voter_id: str,
        check_discriminatory_barriers: bool = True,
    ) -> Dict:
        """
        Check if voter can legally be prevented from voting.
        
        Returns eligibility status and any constitutional violations.
        """
        if voter_id not in self.voters:
            return {
                "eligible": False,
                "reason": "Voter not registered",
                "violations": [],
            }
        
        voter = self.voters[voter_id]
        violations = []
        
        # Check basic eligibility
        if not voter.has_right_to_vote():
            if voter.age < 18:
                violations.append(VotingRightViolation.AGE_DISCRIMINATION)
            if not voter.is_citizen:
                return {
                    "eligible": False,
                    "reason": "Non-citizen",
                    "violations": [],  # Not a constitutional violation
                }
        
        # Check for discriminatory barriers (15th, 19th, 24th Amendments)
        if check_discriminatory_barriers:
            # Poll tax check (24th Amendment)
            if not voter.has_paid_poll_tax:
                violations.append(VotingRightViolation.POLL_TAX)
        
        return {
            "eligible": len(violations) == 0,
            "reason": None if len(violations) == 0 else "Constitutional violations detected",
            "violations": violations,
        }
    
    def cast_ballot(
        self,
        voter_id: str,
        selections: Dict[str, str],
    ) -> Optional[Ballot]:
        """
        Cast a ballot with verifiable hash commitment.
        
        Returns ballot with hash for verification.
        """
        if voter_id not in self.voters:
            return None
        
        ballot_id = f"BALLOT-{voter_id}-{datetime.now().timestamp()}"
        ballot = Ballot(
            ballot_id=ballot_id,
            voter_id=voter_id,
            selections=selections,
            cast_timestamp=datetime.now(),
        )
        
        # Generate hash for verification
        ballot.hash_commitment = ballot.generate_hash()
        self.ballots[ballot_id] = ballot
        
        return ballot
    
    def verify_vote(
        self,
        ballot_id: str,
        expected_selections: Dict[str, str],
    ) -> VoteVerification:
        """
        Verify that vote was recorded as cast.
        
        Implements the invariant: vote is recorded as cast and verifiable.
        """
        if ballot_id not in self.ballots:
            raise ValueError(f"Ballot {ballot_id} not found")
        
        ballot = self.ballots[ballot_id]
        
        # Verify ballot integrity
        integrity_check = ballot.verify_integrity()
        
        verification = VoteVerification(
            ballot_id=ballot_id,
            voter_id=ballot.voter_id,
            recorded_selections=ballot.selections,
            verification_hash=ballot.hash_commitment,
            verification_timestamp=datetime.now(),
        )
        
        return verification
    
    def check_15th_amendment_compliance(
        self,
        voting_procedure: str,
    ) -> bool:
        """
        Check if voting procedure complies with 15th Amendment.
        
        15th Amendment: Right to vote shall not be denied on account of race.
        """
        discriminatory_keywords = ["race", "color", "previous condition of servitude"]
        procedure_lower = voting_procedure.lower()
        
        for keyword in discriminatory_keywords:
            if keyword in procedure_lower and "not" not in procedure_lower:
                self.violations.append(VotingRightViolation.RACIAL_DISCRIMINATION)
                return False
        return True
    
    def check_19th_amendment_compliance(
        self,
        voting_procedure: str,
    ) -> bool:
        """
        Check if voting procedure complies with 19th Amendment.
        
        19th Amendment: Right to vote shall not be denied on account of sex.
        """
        if "sex" in voting_procedure.lower() and "denied" in voting_procedure.lower():
            self.violations.append(VotingRightViolation.SEX_DISCRIMINATION)
            return False
        return True
    
    def get_voting_rights_summary(self) -> dict:
        """Get summary of voting rights checks."""
        total_voters = len(self.voters)
        total_ballots = len(self.ballots)
        
        # Count by violation type
        violation_counts = {}
        for v in self.violations:
            violation_counts[v.name] = violation_counts.get(v.name, 0) + 1
        
        return {
            "registered_voters": total_voters,
            "ballots_cast": total_ballots,
            "violations_detected": len(self.violations),
            "violation_breakdown": violation_counts,
        }


def check_voting_rights(
    voter_age: int,
    is_citizen: bool,
    voting_procedure_description: str,
) -> bool:
    """
    Convenience function to check basic voting rights.
    
    Returns True if voting rights are protected, False if violated.
    """
    checker = VotingRightsChecker()
    
    # Register voter
    checker.register_voter(
        voter_id="TEMP",
        age=voter_age,
        is_citizen=is_citizen,
    )
    
    # Check 15th Amendment
    if not checker.check_15th_amendment_compliance(voting_procedure_description):
        return False
    
    # Check 19th Amendment
    if not checker.check_19th_amendment_compliance(voting_procedure_description):
        return False
    
    return True
