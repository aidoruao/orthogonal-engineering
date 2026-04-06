"""Falsification tests for D_INTERNATIONAL_CRIMINAL

Test ID: F_INTL_CRIMINAL_001 through F_INTL_CRIMINAL_006
Domain: D_INTERNATIONAL_CRIMINAL (International Criminal Law)
Layer: 0 (Supranational)
"""

from datetime import datetime

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_intl_criminal.implementation import (
    InternationalCriminalLaw,
    UniversalJurisdictionCase,
    CoreCrime,
)
from src.domains.d_intl_criminal.invariants import (
    check_universal_jurisdiction_for_core_crimes,
    check_no_prosecution_without_evidence,
    check_icc_complementarity_principle,
    check_all_core_crimes_defined,
)


class TestCoreCrimes:
    """Test suite for CoreCrime enum."""
    
    def test_all_four_crimes_defined(self):
        """F_INTL_CRIMINAL_001: All four Rome Statute crimes are defined."""
        crimes = list(CoreCrime)
        assert len(crimes) == 4
        assert CoreCrime.GENOCIDE in crimes
        assert CoreCrime.CRIMES_AGAINST_HUMANITY in crimes
        assert CoreCrime.WAR_CRIMES in crimes
        assert CoreCrime.AGGRESSION in crimes


class TestUniversalJurisdictionCase:
    """Test suite for UniversalJurisdictionCase."""
    
    def test_can_prosecute_with_evidence_genocide(self):
        """F_INTL_CRIMINAL_002: Genocide case with evidence can be prosecuted."""
        case = UniversalJurisdictionCase(
            case_id="G-001",
            crime=CoreCrime.GENOCIDE,
            suspect="Suspect A",
            location="Test Location",
            evidence_present=True,
        )
        assert case.can_prosecute()
    
    def test_can_prosecute_with_evidence_war_crimes(self):
        """F_INTL_CRIMINAL_003: War crimes case with evidence can be prosecuted."""
        case = UniversalJurisdictionCase(
            case_id="WC-001",
            crime=CoreCrime.WAR_CRIMES,
            suspect="Suspect B",
            location="Battlefield",
            evidence_present=True,
        )
        assert case.can_prosecute()
    
    def test_cannot_prosecute_without_evidence(self):
        """F_INTL_CRIMINAL_004: Case without evidence cannot be prosecuted."""
        case = UniversalJurisdictionCase(
            case_id="NE-001",
            crime=CoreCrime.CRIMES_AGAINST_HUMANITY,
            suspect="Unknown",
            location="Unknown",
            evidence_present=False,
        )
        assert not case.can_prosecute()
    
    def test_cannot_prosecute_aggression_without_evidence(self):
        """F_INTL_CRIMINAL_005: Aggression case without evidence cannot be prosecuted."""
        case = UniversalJurisdictionCase(
            case_id="A-001",
            crime=CoreCrime.AGGRESSION,
            suspect="Leader",
            location="Border",
            evidence_present=False,
        )
        assert not case.can_prosecute()


class TestComplementarity:
    """Test suite for ICC complementarity principle."""
    
    def test_icc_can_prosecute_no_domestic_proceedings(self):
        """F_INTL_CRIMINAL_006: ICC can prosecute if no domestic proceedings."""
        icl = InternationalCriminalLaw()
        
        result = icl.check_complementarity(
            domestic_proceedings=False,
            domestic_willing=False,
            domestic_able=False,
        )
        assert result is True
    
    def test_icc_cannot_prosecute_adequate_domestic(self):
        """F_INTL_CRIMINAL_007: ICC cannot prosecute if domestic proceedings adequate."""
        icl = InternationalCriminalLaw()
        
        result = icl.check_complementarity(
            domestic_proceedings=True,
            domestic_willing=True,
            domestic_able=True,
        )
        assert result is False
    
    def test_icc_can_prosecute_domestic_unwilling(self):
        """F_INTL_CRIMINAL_008: ICC can prosecute if domestic court unwilling."""
        icl = InternationalCriminalLaw()
        
        result = icl.check_complementarity(
            domestic_proceedings=True,
            domestic_willing=False,  # Shielding
            domestic_able=True,
        )
        assert result is True
    
    def test_icc_can_prosecute_domestic_unable(self):
        """F_INTL_CRIMINAL_009: ICC can prosecute if domestic court unable."""
        icl = InternationalCriminalLaw()
        
        result = icl.check_complementarity(
            domestic_proceedings=True,
            domestic_willing=True,
            domestic_able=False,  # Collapsed
        )
        assert result is True
    
    def test_icc_can_prosecute_both_unwilling_and_unable(self):
        """F_INTL_CRIMINAL_010: ICC can prosecute if domestic unwilling and unable."""
        icl = InternationalCriminalLaw()
        
        result = icl.check_complementarity(
            domestic_proceedings=True,
            domestic_willing=False,
            domestic_able=False,
        )
        assert result is True


class TestInvariants:
    """Test invariant checks."""
    
    def test_universal_jurisdiction_for_core_crimes(self):
        """Test check_universal_jurisdiction_for_core_crimes invariant."""
        result = check_universal_jurisdiction_for_core_crimes()
        assert result is True
    
    def test_no_prosecution_without_evidence(self):
        """Test check_no_prosecution_without_evidence invariant."""
        result = check_no_prosecution_without_evidence()
        assert result is True
    
    def test_icc_complementarity_principle(self):
        """Test check_icc_complementarity_principle invariant."""
        result = check_icc_complementarity_principle()
        assert result is True
    
    def test_all_core_crimes_defined(self):
        """Test check_all_core_crimes_defined invariant."""
        result = check_all_core_crimes_defined()
        assert result is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestCoreCrimes().test_all_four_crimes_defined,
        TestUniversalJurisdictionCase().test_can_prosecute_with_evidence_genocide,
        TestUniversalJurisdictionCase().test_cannot_prosecute_without_evidence,
        TestComplementarity().test_icc_can_prosecute_no_domestic_proceedings,
        TestComplementarity().test_icc_cannot_prosecute_adequate_domestic,
        TestComplementarity().test_icc_can_prosecute_domestic_unwilling,
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
