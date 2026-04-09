#!/usr/bin/env python3
"""Election Law Invariants — Eligibility, custody, recounts."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    EligibilityVerifier, BallotCustodyTracker, RecountAnalyzer
)


def check_one_person_one_vote(verifier: EligibilityVerifier) -> Tuple[bool, ProofObject]:
    """One person, one vote: eligible voters must not have voted yet."""
    if verifier.voter.voted:
        return False, ProofObject(
            conclusion="VIOLATION: Voter already voted",
            premises=[],
            rule="one_person_one_vote"
        )
    
    if not verifier.voter.registered:
        return False, ProofObject(
            conclusion="VIOLATION: Voter not registered",
            premises=[],
            rule="voter_registration"
        )
    
    return True, ProofObject(
        conclusion="Voter eligible (registered, not yet voted)",
        premises=[],
        rule="one_person_one_vote"
    )


def check_custody_chain_unbroken(tracker: BallotCustodyTracker) -> Tuple[bool, ProofObject]:
    """Ballot chain of custody must be unbroken."""
    if not tracker.chain_unbroken():
        return False, ProofObject(
            conclusion="VIOLATION: Chain of custody broken",
            premises=[],
            rule="custody_chain"
        )
    
    if not tracker.ballot_count_consistent():
        return False, ProofObject(
            conclusion="VIOLATION: Ballot count inconsistency in custody chain",
            premises=[],
            rule="custody_count"
        )
    
    return True, ProofObject(
        conclusion="Chain of custody intact",
        premises=[f"Links: {len(tracker.custody_chain)}"],
        rule="custody_chain"
    )


def check_recount_threshold(analyzer: RecountAnalyzer) -> Tuple[bool, ProofObject]:
    """Recount triggered when margin < 0.5%."""
    margin = analyzer.winning_margin()
    threshold = analyzer.RECOUNT_THRESHOLD_PCT
    
    if analyzer.recount_required():
        return False, ProofObject(
            conclusion=f"RECOUNT REQUIRED: Margin {margin*100}% < {threshold}% threshold",
            premises=[],
            rule="recount_threshold"
        )
    
    return True, ProofObject(
        conclusion=f"Recount not required (margin {margin*100}% >= {threshold}%)",
        premises=[],
        rule="recount_threshold"
    )


def check_eligibility_before_voting(verifier: EligibilityVerifier) -> Tuple[bool, ProofObject]:
    """Eligibility must be verified before voting."""
    if not verifier.is_eligible():
        return False, ProofObject(
            conclusion="VIOLATION: Ineligible voter attempting to vote",
            premises=[f"Registered: {verifier.voter.registered}", f"Already voted: {verifier.voter.voted}"],
            rule="eligibility_verification"
        )
    
    return True, ProofObject(
        conclusion="Eligibility verified",
        premises=[],
        rule="eligibility_verification"
    )
