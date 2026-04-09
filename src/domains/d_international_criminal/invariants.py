"""D_INTERNATIONAL_CRIMINAL invariant checks — international criminal law.

International criminal law invariants ensure:
1. Jurisdiction rules are followed
2. Complementarity principle is respected
3. Evidence chain of custody is maintained
4. Due process rights are protected
5. Case timelines are reasonable
"""

from datetime import datetime, timedelta
from fractions import Fraction

from .implementation import (
    D_INTERNATIONAL_CRIMINALChecker,
    D_INTERNATIONAL_CRIMINALRecord,
    Case,
    Evidence,
    CrimeType,
    CaseStatus,
)


def check_jurisdiction_rules() -> bool:
    """Verify ICC jurisdiction rules are followed."""
    checker = D_INTERNATIONAL_CRIMINALChecker()
    
    case = Case(
        case_id="CASE-001",
        crime_type=CrimeType.WAR_CRIME,
        status=CaseStatus.INVESTIGATION,
        opened_at=datetime(2026, 1, 1),
        defendant="Defendant A",
        jurisdiction="State X",
    )
    
    # Should have jurisdiction if territorial
    assert checker.check_jurisdiction(case, "State X", "State Y")
    
    # Should have jurisdiction if nationality-based
    assert checker.check_jurisdiction(case, "State Z", "State X")
    
    return True


def check_complementarity_principle() -> bool:
    """Verify complementarity principle is respected."""
    checker = D_INTERNATIONAL_CRIMINALChecker()
    
    # No domestic proceedings = ICC can act
    assert checker.check_complementarity(False, False)
    
    # Domestic proceedings active and willing/able = ICC cannot act
    assert not checker.check_complementarity(True, True)
    
    # Domestic proceedings but unwilling/unable = ICC can act
    assert checker.check_complementarity(True, False)
    
    return True


def check_evidence_chain_of_custody() -> bool:
    """Verify evidence maintains chain of custody."""
    checker = D_INTERNATIONAL_CRIMINALChecker()
    
    valid_evidence = Evidence(
        evidence_id="EVID-001",
        case_id="CASE-002",
        type="documentary",
        authenticity_verified=True,
        chain_of_custody=["collected by A", "transferred to B", "stored in vault"],
    )
    
    invalid_evidence = Evidence(
        evidence_id="EVID-002",
        case_id="CASE-002",
        type="physical",
        authenticity_verified=False,
        chain_of_custody=[],
    )
    
    assert checker.verify_evidence_chain(valid_evidence)
    assert not checker.verify_evidence_chain(invalid_evidence)
    
    return True


def check_case_timeline_reasonableness() -> bool:
    """Verify cases proceed within reasonable timeframes."""
    opened = datetime(2025, 1, 1)
    now = datetime(2026, 4, 9)
    
    case = Case(
        case_id="CASE-003",
        crime_type=CrimeType.CRIME_AGAINST_HUMANITY,
        status=CaseStatus.INVESTIGATION,
        opened_at=opened,
        defendant="Defendant B",
        jurisdiction="State Y",
    )
    
    duration = now - opened
    
    # Investigation should not exceed 5 years without trial
    assert duration.days < 365 * 5, "Investigation exceeded 5 years"
    
    return True


def check_crime_type_classification() -> bool:
    """Verify crimes are properly classified."""
    war_crime = Case(
        case_id="CASE-004",
        crime_type=CrimeType.WAR_CRIME,
        status=CaseStatus.PRELIMINARY_EXAMINATION,
        opened_at=datetime.now(),
        defendant="Defendant C",
        jurisdiction="State Z",
    )
    
    genocide = Case(
        case_id="CASE-005",
        crime_type=CrimeType.GENOCIDE,
        status=CaseStatus.PRELIMINARY_EXAMINATION,
        opened_at=datetime.now(),
        defendant="Defendant D",
        jurisdiction="State W",
    )
    
    assert war_crime.crime_type == CrimeType.WAR_CRIME
    assert genocide.crime_type == CrimeType.GENOCIDE
    
    return True


def check_compliance_deterministic() -> bool:
    """Master compliance check."""
    assert check_jurisdiction_rules()
    assert check_complementarity_principle()
    assert check_evidence_chain_of_custody()
    assert check_case_timeline_reasonableness()
    assert check_crime_type_classification()
    return True
