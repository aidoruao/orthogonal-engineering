"""Falsification tests for D_JUDICIAL_REVIEW

Test ID: F_JUDICIAL_001 through F_JUDICIAL_008
Domain: D_JUDICIAL_REVIEW
Layer: 1 (Constitutional)
"""

from fractions import Fraction
from datetime import datetime

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_judicial_review.implementation import (
    JudicialReview,
    SitusIndependence,
    ChallengeGround,
    ReviewOutcome,
)


class TestJudicialReview:
    """Test suite for JudicialReview."""
    
    def test_any_statute_can_be_challenged(self):
        """F_JUDICIAL_001: Any statute can be challenged."""
        review = JudicialReview()
        
        challenge = review.file_challenge(
            challenge_id="CH-001",
            statute_name="Test Act",
            enacting_branch="legislative",
            grounds=[ChallengeGround.DUE_PROCESS],
        )
        assert challenge.can_be_reviewed() is True
    
    def test_independent_situs_required(self):
        """F_JUDICIAL_002: Independent situs required for review."""
        review = JudicialReview()
        
        review.file_challenge(
            challenge_id="IND-TEST",
            statute_name="Test Act",
            enacting_branch="legislative",
            grounds=[ChallengeGround.FIRST_AMENDMENT],
        )
        
        # Non-independent situs
        situs = SitusIndependence(
            court_name="Legislative Panel",
            enacting_branch_involved=True,
        )
        review.challenges["IND-TEST"].situs = situs
        
        assert review.challenges["IND-TEST"].is_valid_situs() is False
    
    def test_independent_situs_valid(self):
        """F_JUDICIAL_003: Independent situs is valid."""
        review = JudicialReview()
        
        review.file_challenge(
            challenge_id="VALID-TEST",
            statute_name="Test Act",
            enacting_branch="legislative",
            grounds=[ChallengeGround.FOURTH_AMENDMENT],
        )
        
        review.assign_independent_situs("VALID-TEST", "Federal Court")
        assert review.challenges["VALID-TEST"].is_valid_situs() is True
    
    def test_unconstitutional_statute_invalidated(self):
        """F_JUDICIAL_004: Unconstitutional statutes are invalidated."""
        review = JudicialReview()
        
        review.file_challenge(
            challenge_id="INVALIDATE",
            statute_name="Bad Act",
            enacting_branch="executive",
            grounds=[ChallengeGround.SEPARATION_OF_POWERS],
        )
        review.assign_independent_situs("INVALIDATE", "Supreme Court")
        
        outcome = review.conduct_review(
            challenge_id="INVALIDATE",
            statute_unconstitutional=True,
            reasoning="Violates Constitution",
        )
        
        assert outcome == ReviewOutcome.FULLY_INVALIDATED
        assert review.is_statute_valid("Bad Act") is False
    
    def test_constitutional_statute_upheld(self):
        """F_JUDICIAL_005: Constitutional statutes are upheld."""
        review = JudicialReview()
        
        review.file_challenge(
            challenge_id="UPHOLD",
            statute_name="Good Act",
            enacting_branch="legislative",
            grounds=[ChallengeGround.DUE_PROCESS],
        )
        review.assign_independent_situs("UPHOLD", "District Court")
        
        outcome = review.conduct_review(
            challenge_id="UPHOLD",
            statute_unconstitutional=False,
            reasoning="Constitutional",
        )
        
        assert outcome == ReviewOutcome.UPHELD


class TestSitusIndependence:
    """Test suite for SitusIndependence."""
    
    def test_fully_independent_situs(self):
        """F_JUDICIAL_006: Fully independent situs is valid."""
        situs = SitusIndependence(
            court_name="Independent Court",
            enacting_branch_involved=False,
            judicial_independence_score=Fraction(1, 1),
        )
        assert situs.is_independent() is True
    
    def test_non_independent_situs(self):
        """F_JUDICIAL_007: Non-independent situs is invalid."""
        situs = SitusIndependence(
            court_name="Biased Panel",
            enacting_branch_involved=True,
        )
        assert situs.is_independent() is False


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestJudicialReview().test_any_statute_can_be_challenged,
        TestJudicialReview().test_independent_situs_required,
        TestJudicialReview().test_unconstitutional_statute_invalidated,
        TestSitusIndependence().test_fully_independent_situs,
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
