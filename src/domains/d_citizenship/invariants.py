"""D_CITIZENSHIP invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: 14th Amendment, Article I Section 8
"""

from datetime import datetime
from src.domains.d_citizenship.implementation import (
    CitizenshipChecker,
    Citizen,
    NaturalizationProcess,
    CitizenshipStatus,
    BirthrightStatus,
    check_birthright_citizenship,
)


def check_14th_amendment_birthright_citizenship() -> bool:
    """
    Invariant: Birth on US soil confers citizenship (14th Amendment).
    Falsification: If US-born person is not recognized as citizen.
    """
    checker = CitizenshipChecker()
    
    citizen = checker.register_birthright_citizen(
        citizen_id="BIRTHRIGHT-001",
        name="Jane Doe",
        birth_date=datetime(1990, 1, 1),
        birthplace="US",
    )
    
    assert citizen.is_birthright_citizen() is True, (
        "US-born person should be birthright citizen"
    )
    assert citizen.citizenship_status == CitizenshipStatus.BIRTHRIGHT
    assert citizen.birthright_status == BirthrightStatus.BORN_ON_US_SOIL
    
    return True


def check_naturalization_requires_residency() -> bool:
    """
    Invariant: Naturalization requires residency (typically 5 years).
    Falsification: If naturalization granted with insufficient residency.
    """
    process = NaturalizationProcess(
        applicant_id="APPLICANT-001",
        application_date=datetime.now(),
        lawful_permanent_resident=True,
        years_of_residency=3,  # Not enough
        required_residency=5,
    )
    
    # Set other requirements
    process.good_moral_character = True
    process.english_proficiency = True
    process.civics_knowledge = True
    
    assert process.meets_residency_requirement() is False, (
        "3 years should not meet 5-year requirement"
    )
    assert process.is_eligible() is False, (
        "Should not be eligible with insufficient residency"
    )
    
    return True


def check_naturalization_eligibility_requirements() -> bool:
    """
    Invariant: Naturalization requires all eligibility criteria.
    Falsification: If naturalization approved without all requirements.
    """
    checker = CitizenshipChecker()
    
    process = checker.start_naturalization(
        applicant_id="ELIGIBLE-001",
        lawful_permanent_resident=True,
        years_of_residency=5,
    )
    
    # Set all requirements
    process.good_moral_character = True
    process.english_proficiency = True
    process.civics_knowledge = True
    
    assert process.is_eligible() is True, (
        "Should be eligible with all requirements met"
    )
    
    return True


def check_birthright_citizen_cannot_be_denaturalized() -> bool:
    """
    Invariant: Birthright citizenship cannot be revoked (only renounced).
    Falsification: If birthright citizen is subject to denaturalization.
    """
    checker = CitizenshipChecker()
    
    citizen = checker.register_birthright_citizen(
        citizen_id="BIRTHRIGHT-IMMUNE",
        name="John Smith",
        birth_date=datetime(1985, 6, 15),
        birthplace="US",
    )
    
    assert citizen.can_be_denaturalized() is False, (
        "Birthright citizen should not be subject to denaturalization"
    )
    
    # Attempt denaturalization should fail
    result = checker.attempt_denaturalization(
        citizen_id="BIRTHRIGHT-IMMUNE",
        due_process_notice=True,
        due_process_hearing=True,
    )
    
    assert result["success"] is False, (
        "Denaturalization of birthright citizen should fail"
    )
    
    return True


def check_denaturalization_requires_due_process() -> bool:
    """
    Invariant: Denaturalization requires due process (notice + hearing).
    Falsification: If denaturalization succeeds without due process.
    """
    checker = CitizenshipChecker()
    
    # Create naturalized citizen
    naturalized = Citizen(
        citizen_id="NATURALIZED-001",
        name="Maria Garcia",
        birth_date=datetime(1970, 3, 10),
        citizenship_status=CitizenshipStatus.NATURALIZED,
        birthright_status=BirthrightStatus.NOT_BIRTHRIGHT,
        naturalization_date=datetime(2000, 1, 1),
    )
    checker.citizens["NATURALIZED-001"] = naturalized
    
    # Attempt denaturalization without due process
    result = checker.attempt_denaturalization(
        citizen_id="NATURALIZED-001",
        due_process_notice=False,  # No notice
        due_process_hearing=False,  # No hearing
    )
    
    assert result["success"] is False, (
        "Denaturalization without due process should fail"
    )
    assert result["due_process_violation"] is True
    
    return True


def check_birthright_citizenship_function() -> bool:
    """
    Invariant: Birthright citizenship function correctly identifies US birth.
    Falsification: If birthplace check returns wrong result.
    """
    assert check_birthright_citizenship("US") is True
    assert check_birthright_citizenship("Mexico") is False
    assert check_birthright_citizenship("Canada") is False
    
    return True


def check_14th_amendment_law_compliance() -> bool:
    """
    Invariant: Citizenship laws comply with 14th Amendment.
    Falsification: If law denying birthright citizenship is approved.
    """
    checker = CitizenshipChecker()
    
    result = checker.check_14th_amendment_compliance(
        "Deny citizenship to children born on US soil"
    )
    
    assert result is False, (
        "Law denying birthright citizenship should violate 14th Amendment"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_CITIZENSHIP invariants."""
    checks = [
        check_14th_amendment_birthright_citizenship,
        check_naturalization_requires_residency,
        check_naturalization_eligibility_requirements,
        check_birthright_citizen_cannot_be_denaturalized,
        check_denaturalization_requires_due_process,
        check_birthright_citizenship_function,
        check_14th_amendment_law_compliance,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_CITIZENSHIP invariants: PASS")
