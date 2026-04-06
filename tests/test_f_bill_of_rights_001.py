"""Falsification tests for D_BILL_OF_RIGHTS

Test ID: F_BOR_001 through F_BOR_010
Domain: D_BILL_OF_RIGHTS (Bill of Rights)
Layer: 1 (Constitutional)
"""

from fractions import Fraction

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_bill_of_rights.implementation import (
    BillOfRightsChecker,
    FirstAmendmentRights,
    FourthAmendmentRights,
    DueProcessRights,
    RightsViolation,
)
from src.domains.d_bill_of_rights.invariants import (
    check_first_amendment_protects_political_speech,
    check_fourth_amendment_requires_warrant_for_home,
    check_due_process_requires_notice_and_hearing,
)


class TestFirstAmendment:
    """Test suite for First Amendment rights."""
    
    def test_political_speech_protected(self):
        """F_BOR_001: Political speech is protected."""
        rights = FirstAmendmentRights(
            speech_content="Criticism of government policy",
        )
        assert rights.is_protected_speech() is True
    
    def test_incitement_not_protected(self):
        """F_BOR_002: Incitement is not protected speech."""
        rights = FirstAmendmentRights(
            speech_content="Incitement to violence against a group",
        )
        assert rights.is_protected_speech() is False
    
    def test_religious_exercise_protected(self):
        """F_BOR_003: Religious exercise is protected."""
        rights = FirstAmendmentRights(
            speech_content="Religious practice",
            is_religious=True,
        )
        assert rights.free_exercise_applies() is True


class TestFourthAmendment:
    """Test suite for Fourth Amendment rights."""
    
    def test_warrant_makes_search_reasonable(self):
        """F_BOR_004: Warrant makes search reasonable."""
        rights = FourthAmendmentRights(
            has_warrant=True,
            probable_cause=True,
            search_location="home",
        )
        assert rights.is_reasonable_search() is True
    
    def test_home_requires_warrant(self):
        """F_BOR_005: Home search requires warrant."""
        rights = FourthAmendmentRights(
            has_warrant=False,
            search_location="home",
        )
        assert rights.requires_warrant() is True
    
    def test_consent_validates_search(self):
        """F_BOR_006: Consent validates warrantless search."""
        rights = FourthAmendmentRights(
            has_warrant=False,
            search_location="home",
            consent_given=True,
        )
        assert rights.is_reasonable_search() is True
    
    def test_exigent_circumstances_exception(self):
        """F_BOR_007: Exigent circumstances allow warrantless entry."""
        rights = FourthAmendmentRights(
            has_warrant=False,
            search_location="home",
            probable_cause=True,
            exigent_circumstances=True,
        )
        assert rights.is_reasonable_search() is True


class TestDueProcess:
    """Test suite for Due Process rights."""
    
    def test_notice_and_hearing_satisfies_due_process(self):
        """F_BOR_008: Notice and hearing satisfy due process."""
        rights = DueProcessRights(
            deprivation_type="property",
            notice_given=True,
            hearing_held=True,
        )
        assert rights.is_due_process_violation() is False
    
    def test_no_notice_violates_due_process(self):
        """F_BOR_009: No notice violates due process."""
        rights = DueProcessRights(
            deprivation_type="liberty",
            notice_given=False,
            hearing_held=True,
        )
        assert rights.is_due_process_violation() is True
    
    def test_arbitrary_action_violates_due_process(self):
        """F_BOR_010: Arbitrary action violates due process."""
        rights = DueProcessRights(
            deprivation_type="property",
            notice_given=True,
            hearing_held=True,
            arbitrary_action=True,
        )
        assert rights.is_due_process_violation() is True


class TestBillOfRightsChecker:
    """Test suite for BillOfRightsChecker."""
    
    def test_check_first_amendment(self):
        """Test first amendment checking."""
        checker = BillOfRightsChecker()
        result = checker.check_first_amendment(
            speech_content="Political speech",
            law_name="Test Law",
            restricts_speech=True,
        )
        assert isinstance(result.compliant, bool)
    
    def test_check_fourth_amendment(self):
        """Test fourth amendment checking."""
        checker = BillOfRightsChecker()
        result = checker.check_fourth_amendment(
            search_location="home",
            has_warrant=True,
            probable_cause=True,
            law_name="Test Law",
        )
        assert result.compliant is True
    
    def test_check_due_process(self):
        """Test due process checking."""
        checker = BillOfRightsChecker()
        result = checker.check_due_process(
            deprivation_type="liberty",
            notice_given=False,
            hearing_held=False,
            law_name="Test Law",
        )
        assert result.compliant is False
        assert RightsViolation.DUE_PROCESS in result.violated_rights


class TestInvariants:
    """Test invariant checks."""
    
    def test_first_amendment_protects_political_speech(self):
        """Test check_first_amendment_protects_political_speech."""
        result = check_first_amendment_protects_political_speech()
        assert result is True
    
    def test_fourth_amendment_requires_warrant_for_home(self):
        """Test check_fourth_amendment_requires_warrant_for_home."""
        result = check_fourth_amendment_requires_warrant_for_home()
        assert result is True
    
    def test_due_process_requires_notice_and_hearing(self):
        """Test check_due_process_requires_notice_and_hearing."""
        result = check_due_process_requires_notice_and_hearing()
        assert result is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestFirstAmendment().test_political_speech_protected,
        TestFirstAmendment().test_incitement_not_protected,
        TestFourthAmendment().test_warrant_makes_search_reasonable,
        TestFourthAmendment().test_consent_validates_search,
        TestDueProcess().test_notice_and_hearing_satisfies_due_process,
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
