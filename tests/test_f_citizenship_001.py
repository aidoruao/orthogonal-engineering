"""Falsification tests for D_CITIZENSHIP

Test ID: F_CITIZENSHIP_001 through F_CITIZENSHIP_008
Domain: D_CITIZENSHIP
Layer: 1 (Constitutional)
"""

from datetime import datetime

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_citizenship.implementation import (
    CitizenshipChecker,
    Citizen,
    NaturalizationProcess,
    CitizenshipStatus,
    BirthrightStatus,
    check_birthright_citizenship,
)


class TestBirthrightCitizenship:
    """Test suite for birthright citizenship."""
    
    def test_born_on_us_soil_is_citizen(self):
        """F_CITIZENSHIP_001: Born on US soil = citizen (14th Amendment)."""
        checker = CitizenshipChecker()
        
        citizen = checker.register_birthright_citizen(
            citizen_id="BIRTH-001",
            name="Jane Doe",
            birth_date=datetime(1990, 1, 1),
            birthplace="US",
        )
        
        assert citizen.is_birthright_citizen() is True
        assert citizen.birthright_status == BirthrightStatus.BORN_ON_US_SOIL
    
    def test_foreign_birth_not_birthright(self):
        """F_CITIZENSHIP_002: Foreign birth without US parents = not birthright."""
        checker = CitizenshipChecker()
        
        citizen = checker.register_birthright_citizen(
            citizen_id="BIRTH-002",
            name="Maria Garcia",
            birth_date=datetime(1985, 6, 15),
            birthplace="Mexico",
            parent_citizenship="Mexico",
        )
        
        assert citizen.birthright_status == BirthrightStatus.NOT_BIRTHRIGHT


class TestNaturalization:
    """Test suite for naturalization."""
    
    def test_naturalization_requires_residency(self):
        """F_CITIZENSHIP_003: Naturalization requires residency."""
        process = NaturalizationProcess(
            applicant_id="APP-001",
            application_date=datetime.now(),
            lawful_permanent_resident=True,
            years_of_residency=3,
            required_residency=5,
        )
        
        assert process.meets_residency_requirement() is False
    
    def test_naturalization_eligibility(self):
        """F_CITIZENSHIP_004: Naturalization requires all criteria."""
        checker = CitizenshipChecker()
        
        process = checker.start_naturalization(
            applicant_id="APP-002",
            lawful_permanent_resident=True,
            years_of_residency=5,
        )
        
        # Without requirements set
        assert process.is_eligible() is False
        
        # Set all requirements
        process.good_moral_character = True
        process.english_proficiency = True
        process.civics_knowledge = True
        
        assert process.is_eligible() is True


class TestDenaturalization:
    """Test suite for denaturalization."""
    
    def test_birthright_citizen_cannot_be_denaturalized(self):
        """F_CITIZENSHIP_005: Birthright citizen cannot be denaturalized."""
        checker = CitizenshipChecker()
        
        citizen = checker.register_birthright_citizen(
            citizen_id="BIRTH-IMMUNE",
            name="John Smith",
            birth_date=datetime(1980, 3, 10),
            birthplace="US",
        )
        
        assert citizen.can_be_denaturalized() is False
        
        result = checker.attempt_denaturalization(
            citizen_id="BIRTH-IMMUNE",
            due_process_notice=True,
            due_process_hearing=True,
        )
        
        assert result["success"] is False
    
    def test_denaturalization_requires_due_process(self):
        """F_CITIZENSHIP_006: Denaturalization requires due process."""
        checker = CitizenshipChecker()
        
        # Create naturalized citizen
        naturalized = Citizen(
            citizen_id="NAT-001",
            name="Naturalized Citizen",
            birth_date=datetime(1970, 1, 1),
            citizenship_status=CitizenshipStatus.NATURALIZED,
            birthright_status=BirthrightStatus.NOT_BIRTHRIGHT,
            naturalization_date=datetime(2000, 1, 1),
        )
        checker.citizens["NAT-001"] = naturalized
        
        # Attempt without due process
        result = checker.attempt_denaturalization(
            citizen_id="NAT-001",
            due_process_notice=False,
            due_process_hearing=False,
        )
        
        assert result["success"] is False
        assert result["due_process_violation"] is True


class TestBirthrightFunction:
    """Test suite for birthright citizenship function."""
    
    def test_birthright_function_us_birth(self):
        """F_CITIZENSHIP_007: Function returns True for US birth."""
        assert check_birthright_citizenship("US") is True
    
    def test_birthright_function_foreign_birth(self):
        """F_CITIZENSHIP_008: Function returns False for foreign birth."""
        assert check_birthright_citizenship("Canada") is False


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestBirthrightCitizenship().test_born_on_us_soil_is_citizen,
        TestNaturalization().test_naturalization_requires_residency,
        TestDenaturalization().test_birthright_citizen_cannot_be_denaturalized,
        TestBirthrightFunction().test_birthright_function_us_birth,
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
