"""Falsification tests for D_VOTING_RIGHTS

Test ID: F_VOTING_001 through F_VOTING_010
Domain: D_VOTING_RIGHTS
Layer: 1 (Constitutional)
"""

from datetime import datetime

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_voting_rights.implementation import (
    VotingRightsChecker,
    Voter,
    VotingRightViolation,
    check_voting_rights,
)


class TestVotingEligibility:
    """Test suite for voting eligibility."""
    
    def test_age_18_can_vote(self):
        """F_VOTING_001: 18-year-old citizen can vote (26th Amendment)."""
        checker = VotingRightsChecker()
        voter = checker.register_voter(
            voter_id="VOTER-18",
            age=18,
            is_citizen=True,
        )
        assert voter.has_right_to_vote() is True
    
    def test_age_17_cannot_vote(self):
        """F_VOTING_002: 17-year-old cannot vote."""
        checker = VotingRightsChecker()
        voter = checker.register_voter(
            voter_id="VOTER-17",
            age=17,
            is_citizen=True,
        )
        assert voter.has_right_to_vote() is False
    
    def test_non_citizen_cannot_vote(self):
        """F_VOTING_003: Non-citizen cannot vote."""
        checker = VotingRightsChecker()
        voter = checker.register_voter(
            voter_id="NON-CITIZEN",
            age=25,
            is_citizen=False,
        )
        assert voter.has_right_to_vote() is False


class TestVotingRightsAmendments:
    """Test suite for voting rights amendments."""
    
    def test_15th_amendment_no_race_discrimination(self):
        """F_VOTING_004: 15th Amendment prohibits racial discrimination."""
        checker = VotingRightsChecker()
        
        result = checker.check_15th_amendment_compliance(
            "Voting denied based on race"
        )
        assert result is False
        assert VotingRightViolation.RACIAL_DISCRIMINATION in checker.violations
    
    def test_19th_amendment_no_sex_discrimination(self):
        """F_VOTING_005: 19th Amendment prohibits sex discrimination."""
        checker = VotingRightsChecker()
        
        result = checker.check_19th_amendment_compliance(
            "Voting denied on account of sex"
        )
        assert result is False
        assert VotingRightViolation.SEX_DISCRIMINATION in checker.violations
    
    def test_24th_amendment_no_poll_tax(self):
        """F_VOTING_006: 24th Amendment prohibits poll tax."""
        checker = VotingRightsChecker()
        
        voter = checker.register_voter("POLL-TAX-VOTER", age=25, is_citizen=True)
        voter.has_paid_poll_tax = False
        
        result = checker.check_voting_eligibility("POLL-TAX-VOTER")
        
        has_poll_tax_violation = any(
            v == VotingRightViolation.POLL_TAX for v in result["violations"]
        )
        assert has_poll_tax_violation is True


class TestVoteVerification:
    """Test suite for vote verification."""
    
    def test_vote_recorded_as_cast(self):
        """F_VOTING_007: Vote is recorded as cast."""
        checker = VotingRightsChecker()
        
        checker.register_voter("V001", age=25, is_citizen=True)
        ballot = checker.cast_ballot(
            voter_id="V001",
            selections={"President": "Candidate A"},
        )
        
        assert ballot.voter_id == "V001"
        assert ballot.selections == {"President": "Candidate A"}
    
    def test_ballot_integrity_verification(self):
        """F_VOTING_008: Ballot integrity can be verified."""
        checker = VotingRightsChecker()
        
        checker.register_voter("V002", age=30, is_citizen=True)
        ballot = checker.cast_ballot(
            voter_id="V002",
            selections={"Senator": "Candidate B"},
        )
        
        assert ballot.verify_integrity() is True
    
    def test_vote_matches_voter_intent(self):
        """F_VOTING_009: Vote matches voter intent."""
        checker = VotingRightsChecker()
        
        checker.register_voter("V003", age=35, is_citizen=True)
        ballot = checker.cast_ballot(
            voter_id="V003",
            selections={"Governor": "Candidate C"},
        )
        
        verification = checker.verify_vote(
            ballot_id=ballot.ballot_id,
            expected_selections={"Governor": "Candidate C"},
        )
        
        assert verification.matches_voter_intent({"Governor": "Candidate C"}) is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestVotingEligibility().test_age_18_can_vote,
        TestVotingEligibility().test_age_17_cannot_vote,
        TestVotingRightsAmendments().test_15th_amendment_no_race_discrimination,
        TestVoteVerification().test_vote_recorded_as_cast,
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
