"""Falsification tests for D_HABEAS_CORPUS

Test ID: F_HABEAS_001 through F_HABEAS_008
Domain: D_HABEAS_CORPUS
Layer: 1 (Constitutional)
"""

from datetime import datetime

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_habeas_corpus.implementation import (
    HabeasCorpusChecker,
    DetentionCase,
    DetentionType,
    SuspensionStatus,
    HabeasPetition,
    HabeasStatus,
    check_habeas_corpus_available,
)


class TestHabeasAvailability:
    """Test suite for habeas corpus availability."""
    
    def test_habeas_available_by_default(self):
        """F_HABEAS_001: Habeas corpus available by default."""
        checker = HabeasCorpusChecker()
        
        checker.register_detention(
            case_id="DET-001",
            detainee_name="John Doe",
            detention_type=DetentionType.CRIMINAL,
            detention_location="Jail",
        )
        
        assert checker.can_challenge_detention("DET-001") is True
    
    def test_suspension_requires_rebellion(self):
        """F_HABEAS_002: Valid suspension for rebellion."""
        checker = HabeasCorpusChecker()
        
        result = checker.suspend_habeas_corpus(
            reason="Armed rebellion",
            is_rebellion=True,
        )
        
        assert result["suspended"] is True
        assert result["valid"] is True
        assert checker.suspension_status == SuspensionStatus.SUSPENDED_REBELLION
    
    def test_suspension_requires_invasion(self):
        """F_HABEAS_003: Valid suspension for invasion."""
        checker = HabeasCorpusChecker()
        
        result = checker.suspend_habeas_corpus(
            reason="Foreign invasion",
            is_invasion=True,
        )
        
        assert result["suspended"] is True
        assert result["valid"] is True
        assert checker.suspension_status == SuspensionStatus.SUSPENDED_INVASION
    
    def test_invalid_suspension_rejected(self):
        """F_HABEAS_004: Invalid suspension (no rebellion/invasion) rejected."""
        checker = HabeasCorpusChecker()
        
        result = checker.suspend_habeas_corpus(
            reason="General emergency",
            is_rebellion=False,
            is_invasion=False,
        )
        
        assert result["suspended"] is False
        assert result["valid"] is False


class TestDetentionReview:
    """Test suite for detention review."""
    
    def test_no_detention_without_review(self):
        """F_HABEAS_005: No detention without judicial review."""
        case = DetentionCase(
            case_id="DET-NO-REVIEW",
            detainee_name="Jane Smith",
            detention_type=DetentionType.NATIONAL_SECURITY,
            detention_start=datetime.now(),
            detention_location="Facility",
            criminal_charges=None,
        )
        
        # Without charges or review, detention is not lawful
        assert case.is_lawful_detention() is False
    
    def test_criminal_detention_requires_charges(self):
        """F_HABEAS_006: Criminal detention requires charges."""
        case_with_charges = DetentionCase(
            case_id="DET-CHARGES",
            detainee_name="Defendant",
            detention_type=DetentionType.CRIMINAL,
            detention_start=datetime.now(),
            detention_location="Jail",
            criminal_charges="Burglary",
        )
        
        assert case_with_charges.is_lawful_detention() is True
        
        case_without_charges = DetentionCase(
            case_id="DET-NO-CHARGES",
            detainee_name="Suspect",
            detention_type=DetentionType.CRIMINAL,
            detention_start=datetime.now(),
            detention_location="Jail",
            criminal_charges=None,
        )
        
        assert case_without_charges.is_lawful_detention() is False
    
    def test_habeas_petition_can_be_filed(self):
        """F_HABEAS_007: Habeas petition can be filed."""
        checker = HabeasCorpusChecker()
        
        checker.register_detention(
            case_id="DET-PETITION",
            detainee_name="Bob Johnson",
            detention_type=DetentionType.CRIMINAL,
            detention_location="Prison",
            criminal_charges="Robbery",
        )
        
        petition = checker.file_habeas_petition(
            petition_id="PET-001",
            case_id="DET-PETITION",
            petitioner_name="Bob Johnson",
            grounds="Unlawful detention",
        )
        
        assert petition.petition_id == "PET-001"
        assert petition.status == HabeasStatus.PENDING


class TestAvailabilityFunction:
    """Test suite for availability function."""
    
    def test_available_without_rebellion_invasion(self):
        """F_HABEAS_008: Available without rebellion/invasion."""
        assert check_habeas_corpus_available(
            is_rebellion=False, is_invasion=False
        ) is True
    
    def test_unavailable_with_rebellion(self):
        """Not available during rebellion."""
        assert check_habeas_corpus_available(
            is_rebellion=True, is_invasion=False
        ) is False


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestHabeasAvailability().test_habeas_available_by_default,
        TestHabeasAvailability().test_suspension_requires_rebellion,
        TestHabeasAvailability().test_invalid_suspension_rejected,
        TestDetentionReview().test_criminal_detention_requires_charges,
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
