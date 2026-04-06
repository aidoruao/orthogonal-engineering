"""D_BILL_OF_RIGHTS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: US Constitution Bill of Rights (Amendments 1-10)
"""

from src.domains.d_bill_of_rights.implementation import (
    BillOfRightsChecker,
    FirstAmendmentRights,
    FourthAmendmentRights,
    DueProcessRights,
    RightsViolation,
    check_bill_of_rights_compliance,
)


def check_first_amendment_protects_political_speech() -> bool:
    """
    Invariant: Political speech is protected under First Amendment.
    Falsification: If law restricting political speech is not flagged as violation.
    """
    checker = BillOfRightsChecker()
    
    result = checker.check_first_amendment(
        speech_content="Criticism of government policy",
        law_name="Speech Restriction Act",
        restricts_speech=True,
    )
    
    # A law restricting political speech should be flagged as non-compliant
    # because political speech is protected
    assert not result.compliant, (
        "Law restricting political speech should violate First Amendment"
    )
    assert RightsViolation.FREE_SPEECH in result.violated_rights, (
        "Political speech restriction should be flagged as violation"
    )
    
    return True


def check_unprotected_speech_can_be_restricted() -> bool:
    """
    Invariant: Unprotected speech (incitement) can be restricted.
    Falsification: If incitement to violence is treated as protected speech.
    """
    rights = FirstAmendmentRights(
        speech_content="Incitement to violence against a group",
    )
    
    # Incitement is not protected
    assert not rights.is_protected_speech(), (
        "Incitement to violence should not be protected speech"
    )
    
    return True


def check_fourth_amendment_requires_warrant_for_home() -> bool:
    """
    Invariant: Home searches require warrant under Fourth Amendment.
    Falsification: If warrantless home search is not flagged as violation.
    """
    checker = BillOfRightsChecker()
    
    result = checker.check_fourth_amendment(
        search_location="home",
        has_warrant=False,
        probable_cause=False,
        law_name="Warrantless Search Authorization",
    )
    
    assert not result.compliant, (
        "Warrantless home search should violate Fourth Amendment"
    )
    assert RightsViolation.WARRANTLESS_SEARCH in result.violated_rights, (
        "Warrantless search should be in violations"
    )
    
    return True


def check_consent_validates_search() -> bool:
    """
    Invariant: Consent validates search without warrant.
    Falsification: If consensual search is flagged as violation.
    """
    rights = FourthAmendmentRights(
        has_warrant=False,
        search_location="home",
        consent_given=True,
        probable_cause=False,
    )
    
    assert rights.is_reasonable_search(), (
        "Consensual search should be reasonable"
    )
    
    return True


def check_due_process_requires_notice_and_hearing() -> bool:
    """
    Invariant: Due process requires notice and hearing before deprivation.
    Falsification: If deprivation without notice/hearing is not flagged.
    """
    checker = BillOfRightsChecker()
    
    result = checker.check_due_process(
        deprivation_type="liberty",
        notice_given=False,
        hearing_held=False,
        law_name="Administrative Detention Act",
    )
    
    assert not result.compliant, (
        "Deprivation without notice/hearing should violate due process"
    )
    assert RightsViolation.DUE_PROCESS in result.violated_rights, (
        "Due process violation should be flagged"
    )
    
    return True


def check_due_process_satisfied_with_notice_and_hearing() -> bool:
    """
    Invariant: Due process is satisfied with notice and hearing.
    Falsification: If proper procedure is flagged as violation.
    """
    rights = DueProcessRights(
        deprivation_type="property",
        notice_given=True,
        hearing_held=True,
        fair_procedures=True,
    )
    
    assert not rights.is_due_process_violation(), (
        "Proper notice and hearing should satisfy due process"
    )
    
    return True


def check_exigent_circumstances_exception() -> bool:
    """
    Invariant: Exigent circumstances allow warrantless entry.
    Falsification: If exigent circumstances search is flagged as violation.
    """
    rights = FourthAmendmentRights(
        has_warrant=False,
        search_location="home",
        probable_cause=True,
        exigent_circumstances=True,
    )
    
    assert rights.is_reasonable_search(), (
        "Exigent circumstances should validate search"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_BILL_OF_RIGHTS invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_first_amendment_protects_political_speech,
        check_unprotected_speech_can_be_restricted,
        check_fourth_amendment_requires_warrant_for_home,
        check_consent_validates_search,
        check_due_process_requires_notice_and_hearing,
        check_due_process_satisfied_with_notice_and_hearing,
        check_exigent_circumstances_exception,
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
    print("All D_BILL_OF_RIGHTS invariants: PASS")
