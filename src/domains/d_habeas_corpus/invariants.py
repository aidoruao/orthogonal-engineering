"""D_HABEAS_CORPUS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: US Constitution Article I, Section 9
"""

from datetime import datetime
from src.domains.d_habeas_corpus.implementation import (
    HabeasCorpusChecker,
    DetentionCase,
    DetentionType,
    HabeasPetition,
    SuspensionStatus,
    HabeasStatus,
    check_habeas_corpus_available,
)


def check_habeas_corpus_available_by_default() -> bool:
    """
    Invariant: Habeas corpus is available unless suspended.
    Falsification: If habeas is blocked without suspension.
    """
    checker = HabeasCorpusChecker()
    
    # Register detention
    checker.register_detention(
        case_id="DETENTION-001",
        detainee_name="John Doe",
        detention_type=DetentionType.CRIMINAL,
        detention_location="County Jail",
        criminal_charges="Felony charges",
    )
    
    # Should be able to challenge
    assert checker.can_challenge_detention("DETENTION-001") is True, (
        "Should be able to challenge detention when habeas not suspended"
    )
    
    return True


def check_suspension_requires_rebellion_or_invasion() -> bool:
    """
    Invariant: Suspension requires rebellion or invasion (Article I).
    Falsification: If suspension for other reasons is allowed.
    """
    checker = HabeasCorpusChecker()
    
    # Attempt suspension without rebellion or invasion
    result = checker.suspend_habeas_corpus(
        reason="General emergency",
        is_rebellion=False,
        is_invasion=False,
    )
    
    assert result["suspended"] is False, (
        "Suspension without rebellion/invasion should be rejected"
    )
    assert result["valid"] is False
    assert checker.suspension_status == SuspensionStatus.SUSPENDED_INVALID
    
    return True


def check_valid_suspension_for_rebellion() -> bool:
    """
    Invariant: Rebellion allows valid suspension.
    Falsification: If rebellion suspension is rejected.
    """
    checker = HabeasCorpusChecker()
    
    result = checker.suspend_habeas_corpus(
        reason="Ongoing armed rebellion",
        is_rebellion=True,
        is_invasion=False,
    )
    
    assert result["suspended"] is True, (
        "Rebellion should allow valid suspension"
    )
    assert result["valid"] is True
    assert checker.suspension_status == SuspensionStatus.SUSPENDED_REBELLION
    
    return True


def check_valid_suspension_for_invasion() -> bool:
    """
    Invariant: Invasion allows valid suspension.
    Falsification: If invasion suspension is rejected.
    """
    checker = HabeasCorpusChecker()
    
    result = checker.suspend_habeas_corpus(
        reason="Foreign invasion in progress",
        is_rebellion=False,
        is_invasion=True,
    )
    
    assert result["suspended"] is True, (
        "Invasion should allow valid suspension"
    )
    assert result["valid"] is True
    assert checker.suspension_status == SuspensionStatus.SUSPENDED_INVASION
    
    return True


def check_no_detention_without_judicial_review() -> bool:
    """
    Invariant: No detention without judicial review (habeas core).
    Falsification: If detention is marked lawful without review.
    """
    checker = HabeasCorpusChecker()
    
    # Register detention without charges
    case = checker.register_detention(
        case_id="DETENTION-NO-CHARGES",
        detainee_name="Jane Smith",
        detention_type=DetentionType.NATIONAL_SECURITY,
        detention_location="Federal Facility",
        criminal_charges=None,
    )
    
    # Without judicial review, detention is not lawful
    assert case.is_lawful_detention() is False, (
        "Detention without charges or judicial review should not be lawful"
    )
    
    # Conduct judicial review
    checker.conduct_judicial_review(
        case_id="DETENTION-NO-CHARGES",
        lawful_detention=True,
    )
    
    # After review, detention can be lawful
    assert case.judicial_review_completed is True
    
    return True


def check_habeas_petition_can_be_filed() -> bool:
    """
    Invariant: Habeas petition can be filed for any detention.
    Falsification: If petition filing is blocked.
    """
    checker = HabeasCorpusChecker()
    
    checker.register_detention(
        case_id="DETENTION-PETITION",
        detainee_name="Bob Johnson",
        detention_type=DetentionType.CRIMINAL,
        detention_location="State Prison",
        criminal_charges="Robbery",
    )
    
    petition = checker.file_habeas_petition(
        petition_id="PETITION-001",
        case_id="DETENTION-PETITION",
        petitioner_name="Bob Johnson",
        grounds="Unlawful detention beyond sentence",
    )
    
    assert petition.petition_id == "PETITION-001"
    assert petition.status == HabeasStatus.PENDING
    assert petition.is_timely() is True
    
    return True


def check_criminal_detention_requires_charges() -> bool:
    """
    Invariant: Criminal detention requires charges filed.
    Falsification: If criminal detention without charges is lawful.
    """
    # With charges
    case_with_charges = DetentionCase(
        case_id="WITH-CHARGES",
        detainee_name="Defendant A",
        detention_type=DetentionType.CRIMINAL,
        detention_start=datetime.now(),
        detention_location="Jail",
        criminal_charges="Burglary",
    )
    assert case_with_charges.is_lawful_detention() is True
    
    # Without charges
    case_without_charges = DetentionCase(
        case_id="WITHOUT-CHARGES",
        detainee_name="Defendant B",
        detention_type=DetentionType.CRIMINAL,
        detention_start=datetime.now(),
        detention_location="Jail",
        criminal_charges=None,
    )
    assert case_without_charges.is_lawful_detention() is False
    
    return True


def run_all_invariants() -> dict:
    """Run all D_HABEAS_CORPUS invariants."""
    checks = [
        check_habeas_corpus_available_by_default,
        check_suspension_requires_rebellion_or_invasion,
        check_valid_suspension_for_rebellion,
        check_valid_suspension_for_invasion,
        check_no_detention_without_judicial_review,
        check_habeas_petition_can_be_filed,
        check_criminal_detention_requires_charges,
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
    print("All D_HABEAS_CORPUS invariants: PASS")
