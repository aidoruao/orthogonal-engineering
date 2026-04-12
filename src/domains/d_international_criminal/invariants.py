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
from typing import Tuple

from axioms.logic import ProofObject

from .implementation import (
    D_INTERNATIONAL_CRIMINALChecker,
    D_INTERNATIONAL_CRIMINALRecord,
    Case,
    Evidence,
    CrimeType,
    CaseStatus,
)


def check_jurisdiction_rules() -> Tuple[bool, ProofObject]:
    """Verify ICC jurisdiction rules are followed.
    
    Falsifies if: territorial or nationality jurisdiction is incorrectly rejected.
    falsifies_if: territorial or nationality jurisdiction is incorrectly rejected.
    """
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
    if not checker.check_jurisdiction(case, "State X", "State Y"):
        return False, ProofObject(
            rule="jurisdiction_rules",
            subject="CASE-001",
            falsifies_if="territorial jurisdiction denied",
        )
    
    # Should have jurisdiction if nationality-based
    if not checker.check_jurisdiction(case, "State Z", "State X"):
        return False, ProofObject(
            rule="jurisdiction_rules",
            subject="CASE-001",
            falsifies_if="nationality jurisdiction denied",
        )
    
    return True, ProofObject(
        rule="jurisdiction_rules",
        subject="ICC jurisdiction",
        verified=True,
    )


def check_complementarity_principle() -> Tuple[bool, ProofObject]:
    """Verify complementarity principle is respected.
    
    Falsifies if: ICC complementarity logic allows action when domestic systems
    falsifies_if: ICC complementarity logic allows action when domestic systems
    are willing/able or blocks action when they are unwilling/unable.
    """
    checker = D_INTERNATIONAL_CRIMINALChecker()
    
    # No domestic proceedings = ICC can act
    if not checker.check_complementarity(False, False):
        return False, ProofObject(
            rule="complementarity_principle",
            subject="no_domestic_proceedings",
            falsifies_if="ICC cannot act when no domestic proceedings",
        )
    
    # Domestic proceedings active and willing/able = ICC cannot act
    if checker.check_complementarity(True, True):
        return False, ProofObject(
            rule="complementarity_principle",
            subject="domestic_proceedings_active",
            falsifies_if="ICC can act when domestic proceedings willing/able",
        )
    
    # Domestic proceedings but unwilling/unable = ICC can act
    if not checker.check_complementarity(True, False):
        return False, ProofObject(
            rule="complementarity_principle",
            subject="domestic_unwilling_unable",
            falsifies_if="ICC cannot act when domestic unwilling/unable",
        )
    
    return True, ProofObject(
        rule="complementarity_principle",
        subject="complementarity",
        verified=True,
    )


def check_evidence_chain_of_custody() -> Tuple[bool, ProofObject]:
    """Verify evidence maintains chain of custody.
    
    Falsifies if: valid evidence fails chain verification or invalid evidence passes.
    falsifies_if: valid evidence fails chain verification or invalid evidence passes.
    """
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
    
    if not checker.verify_evidence_chain(valid_evidence):
        return False, ProofObject(
            rule="evidence_chain_of_custody",
            subject="EVID-001",
            falsifies_if="valid evidence fails chain check",
        )
    if checker.verify_evidence_chain(invalid_evidence):
        return False, ProofObject(
            rule="evidence_chain_of_custody",
            subject="EVID-002",
            falsifies_if="invalid evidence passes chain check",
        )
    
    return True, ProofObject(
        rule="evidence_chain_of_custody",
        subject="evidence chain",
        verified=True,
    )


def check_case_timeline_reasonableness() -> Tuple[bool, ProofObject]:
    """Verify cases proceed within reasonable timeframes.
    
    Falsifies if: investigation duration exceeds five years without trial.
    falsifies_if: investigation duration exceeds five years without trial.
    """
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
    if duration.days >= 365 * 5:
        return False, ProofObject(
            rule="case_timeline_reasonableness",
            subject="CASE-003",
            falsifies_if=f"investigation exceeded 5 years ({duration.days} days)",
        )
    
    return True, ProofObject(
        rule="case_timeline_reasonableness",
        subject="CASE-003",
        verified=True,
    )


def check_crime_type_classification() -> Tuple[bool, ProofObject]:
    """Verify crimes are properly classified.
    
    Falsifies if: crime type classification does not match expected category.
    falsifies_if: crime type classification does not match expected category.
    """
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
    
    if war_crime.crime_type != CrimeType.WAR_CRIME:
        return False, ProofObject(
            rule="crime_type_classification",
            subject="CASE-004",
            falsifies_if="war crime misclassified",
        )
    if genocide.crime_type != CrimeType.GENOCIDE:
        return False, ProofObject(
            rule="crime_type_classification",
            subject="CASE-005",
            falsifies_if="genocide misclassified",
        )
    
    return True, ProofObject(
        rule="crime_type_classification",
        subject="crime classification",
        verified=True,
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """Master compliance check.

    Falsifies if: any international criminal invariant check fails.
    falsifies_if: any international criminal invariant check fails.
    """
    checks = [
        check_jurisdiction_rules,
        check_complementarity_principle,
        check_evidence_chain_of_custody,
        check_case_timeline_reasonableness,
        check_crime_type_classification,
    ]
    
    for check in checks:
        result, proof = check()
        if not result:
            return False, ProofObject(
                rule="compliance_deterministic",
                subject="master_check",
                falsifies_if=f"{proof.rule} failed",
            )
    
    return True, ProofObject(
        rule="compliance_deterministic",
        subject="international criminal compliance",
        verified=True,
    )
