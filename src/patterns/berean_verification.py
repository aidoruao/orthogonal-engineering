"""Berean Verification Pattern

Biblical basis: Acts 17:11 — Bereans "received the word with all eagerness,
examining the Scriptures daily to see if these things were so."

Application: Test everything before acceptance. No claim is accepted
without verification. All invariants must have falsification tests.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from enum import Enum, auto


class VerificationStatus(Enum):
    """Status of a verification check."""
    VERIFIED = auto()
    FAILED = auto()
    PENDING = auto()
    NOT_TESTABLE = auto()


@dataclass
class Claim:
    """A claim to be verified."""
    claim_id: str
    statement: str
    source: str
    falsification_condition: str  # How to falsify this claim
    verification_tests: List[Callable[[], bool]] = field(default_factory=list)


class BereanVerification:
    """
    Implements the Berean verification pattern.
    
    All claims must be tested before acceptance. No claim is exempt
    from falsification testing (including theological claims).
    
    Attributes:
        claims: List of claims being tracked
        require_falsification: Whether all claims must have falsification tests
    """
    
    def __init__(self, require_falsification: bool = True):
        self.claims: List[Claim] = []
        self.require_falsification = require_falsification
        self.verification_results: Dict[str, VerificationStatus] = {}
    
    def register_claim(self, claim: Claim) -> None:
        """Register a claim for verification."""
        if self.require_falsification and not claim.falsification_condition:
            raise ValueError(
                f"Claim {claim.claim_id} has no falsification condition. "
                "All claims must be falsifiable per Popperian standard."
            )
        
        self.claims.append(claim)
        self.verification_results[claim.claim_id] = VerificationStatus.PENDING
    
    def verify_claim(self, claim_id: str) -> VerificationStatus:
        """
        Run verification tests for a claim.
        
        Returns:
            VerificationStatus based on test results
        """
        claim = next((c for c in self.claims if c.claim_id == claim_id), None)
        if claim is None:
            raise ValueError(f"Claim {claim_id} not found")
        
        if not claim.verification_tests:
            self.verification_results[claim_id] = VerificationStatus.NOT_TESTABLE
            return VerificationStatus.NOT_TESTABLE
        
        # Run all verification tests
        all_passed = True
        for test in claim.verification_tests:
            try:
                if not test():
                    all_passed = False
                    break
            except Exception:
                all_passed = False
                break
        
        status = VerificationStatus.VERIFIED if all_passed else VerificationStatus.FAILED
        self.verification_results[claim_id] = status
        return status
    
    def verify_all(self) -> Dict[str, VerificationStatus]:
        """Verify all registered claims."""
        for claim in self.claims:
            self.verify_claim(claim.claim_id)
        return self.verification_results.copy()
    
    def get_unverified_claims(self) -> List[Claim]:
        """Get all claims that haven't been verified."""
        return [
            c for c in self.claims
            if self.verification_results.get(c.claim_id) == VerificationStatus.PENDING
        ]
    
    def get_failed_claims(self) -> List[Claim]:
        """Get all claims that failed verification."""
        return [
            c for c in self.claims
            if self.verification_results.get(c.claim_id) == VerificationStatus.FAILED
        ]
