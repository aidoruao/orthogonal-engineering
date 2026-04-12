"""D_HABEAS_CORPUS invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- U.S. Constitution Article I, Section 9 (Suspension Clause)
- 28 U.S.C. §2254 (federal habeas corpus for state prisoners)
- 28 U.S.C. §2255 (federal prisoner motion to vacate)

Source: ontology/ontology.json#D_HABEAS_CORPUS
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple
from datetime import datetime

from axioms.logic import ProofObject

from src.domains.d_habeas_corpus.implementation import (
    HabeasCorpusChecker,
    DetentionCase,
    DetentionType,
    HabeasPetition,
    SuspensionStatus,
    HabeasStatus,
)


def check_habeas_availability_default() -> Tuple[bool, ProofObject]:
    """
    Invariant: Habeas corpus is available by default; no suspension without cause.
    
    Standard: U.S. Constitution Article I, Section 9
    Falsifies if: Habeas is blocked without valid suspension.
    falsifies_if: Habeas is blocked without valid suspension.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
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
    can_challenge = checker.can_challenge_detention("DETENTION-001")
    
    # Suspension status should be NOT_SUSPENDED
    not_suspended = checker.suspension_status == SuspensionStatus.NOT_SUSPENDED
    
    success = can_challenge and not_suspended
    
    proof = ProofObject(
        rule="HabeasAvailabilityDefault",
        premises=[
            f"can_challenge_detention = {can_challenge}",
            f"suspension_status_not_suspended = {not_suspended}",
        ],
        conclusion=(
            "Article I habeas corpus availability enforced"
            if success
            else "FAIL: Habeas corpus not available by default"
        ),
    )
    return success, proof


def check_suspension_requires_rebellion_or_invasion() -> Tuple[bool, ProofObject]:
    """
    Invariant: Suspension requires rebellion or invasion per Article I.
    
    Standard: U.S. Constitution Article I, Section 9
    Falsifies if: Suspension for other reasons is allowed.
    falsifies_if: Suspension for other reasons is allowed.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = HabeasCorpusChecker()
    
    # Attempt suspension without rebellion or invasion
    result = checker.suspend_habeas_corpus(
        reason="General emergency",
        is_rebellion=False,
        is_invasion=False,
    )
    
    suspension_rejected = result["suspended"] is False
    suspension_invalid = result["valid"] is False
    status_invalid = checker.suspension_status == SuspensionStatus.SUSPENDED_INVALID
    
    success = suspension_rejected and suspension_invalid and status_invalid
    
    proof = ProofObject(
        rule="SuspensionRequiresRebellionOrInvasion",
        premises=[
            f"invalid_suspension_rejected = {suspension_rejected}",
            f"suspension_marked_invalid = {suspension_invalid}",
            f"status_suspended_invalid = {status_invalid}",
        ],
        conclusion=(
            "Article I suspension requirements enforced"
            if success
            else "FAIL: Invalid suspension allowed"
        ),
    )
    return success, proof


def check_valid_suspension_rebellion() -> Tuple[bool, ProofObject]:
    """
    Invariant: Rebellion permits valid habeas corpus suspension.
    
    Standard: U.S. Constitution Article I, Section 9
    Falsifies if: Rebellion suspension is rejected.
    falsifies_if: Rebellion suspension is rejected.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = HabeasCorpusChecker()
    
    result = checker.suspend_habeas_corpus(
        reason="Ongoing armed rebellion",
        is_rebellion=True,
        is_invasion=False,
    )
    
    suspended = result["suspended"] is True
    valid = result["valid"] is True
    status_rebellion = checker.suspension_status == SuspensionStatus.SUSPENDED_REBELLION
    basis_correct = result["basis"] == "rebellion"
    
    success = suspended and valid and status_rebellion and basis_correct
    
    proof = ProofObject(
        rule="ValidSuspensionRebellion",
        premises=[
            f"suspended = {suspended}",
            f"valid = {valid}",
            f"status_suspended_rebellion = {status_rebellion}",
            f"basis_rebellion = {basis_correct}",
        ],
        conclusion=(
            "Rebellion suspension properly validated"
            if success
            else "FAIL: Valid rebellion suspension rejected"
        ),
    )
    return success, proof


def check_valid_suspension_invasion() -> Tuple[bool, ProofObject]:
    """
    Invariant: Invasion permits valid habeas corpus suspension.
    
    Standard: U.S. Constitution Article I, Section 9
    Falsifies if: Invasion suspension is rejected.
    falsifies_if: Invasion suspension is rejected.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = HabeasCorpusChecker()
    
    result = checker.suspend_habeas_corpus(
        reason="Foreign invasion in progress",
        is_rebellion=False,
        is_invasion=True,
    )
    
    suspended = result["suspended"] is True
    valid = result["valid"] is True
    status_invasion = checker.suspension_status == SuspensionStatus.SUSPENDED_INVASION
    basis_correct = result["basis"] == "invasion"
    
    success = suspended and valid and status_invasion and basis_correct
    
    proof = ProofObject(
        rule="ValidSuspensionInvasion",
        premises=[
            f"suspended = {suspended}",
            f"valid = {valid}",
            f"status_suspended_invasion = {status_invasion}",
            f"basis_invasion = {basis_correct}",
        ],
        conclusion=(
            "Invasion suspension properly validated"
            if success
            else "FAIL: Valid invasion suspension rejected"
        ),
    )
    return success, proof


def check_judicial_review_required() -> Tuple[bool, ProofObject]:
    """
    Invariant: Non-criminal detention requires judicial review for lawfulness.
    
    Standard: 28 U.S.C. §2254; 28 U.S.C. §2255
    Falsifies if: Detention without charges or review is marked lawful.
    falsifies_if: Detention without charges or review is marked lawful.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = HabeasCorpusChecker()
    
    # Register national security detention without charges
    case = checker.register_detention(
        case_id="DETENTION-NO-CHARGES",
        detainee_name="Jane Smith",
        detention_type=DetentionType.NATIONAL_SECURITY,
        detention_location="Federal Facility",
        criminal_charges=None,
    )
    
    # Without judicial review, detention is not lawful
    unlawful_before_review = case.is_lawful_detention() is False
    
    # Conduct judicial review
    checker.conduct_judicial_review(
        case_id="DETENTION-NO-CHARGES",
        lawful_detention=True,
    )
    
    review_completed = case.judicial_review_completed is True
    review_date_set = case.review_date is not None
    
    success = unlawful_before_review and review_completed and review_date_set
    
    proof = ProofObject(
        rule="JudicialReviewRequired",
        premises=[
            f"unlawful_before_review = {unlawful_before_review}",
            f"review_completed = {review_completed}",
            f"review_date_set = {review_date_set}",
        ],
        conclusion=(
            "28 U.S.C. §2254 judicial review requirements enforced"
            if success
            else "FAIL: Judicial review requirements not enforced"
        ),
    )
    return success, proof


def check_criminal_detention_requires_charges() -> Tuple[bool, ProofObject]:
    """
    Invariant: Criminal detention requires charges filed.
    
    Standard: Fourth Amendment; 28 U.S.C. §2254
    Falsifies if: Criminal detention without charges is lawful.
    falsifies_if: Criminal detention without charges is lawful.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
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
    lawful_with_charges = case_with_charges.is_lawful_detention() is True
    
    # Without charges
    case_without_charges = DetentionCase(
        case_id="WITHOUT-CHARGES",
        detainee_name="Defendant B",
        detention_type=DetentionType.CRIMINAL,
        detention_start=datetime.now(),
        detention_location="Jail",
        criminal_charges=None,
    )
    unlawful_without_charges = case_without_charges.is_lawful_detention() is False
    
    success = lawful_with_charges and unlawful_without_charges
    
    proof = ProofObject(
        rule="CriminalDetentionRequiresCharges",
        premises=[
            f"lawful_with_charges = {lawful_with_charges}",
            f"unlawful_without_charges = {unlawful_without_charges}",
        ],
        conclusion=(
            "Criminal detention charge requirements enforced"
            if success
            else "FAIL: Criminal detention without charges allowed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_HABEAS_CORPUS invariants.

    Falsifies if: any habeas corpus invariant check fails or raises an exception.
    falsifies_if: any habeas corpus invariant check fails or raises an exception.
    """
    checks = [
        ("check_habeas_availability_default", check_habeas_availability_default),
        ("check_suspension_requires_rebellion_or_invasion", check_suspension_requires_rebellion_or_invasion),
        ("check_valid_suspension_rebellion", check_valid_suspension_rebellion),
        ("check_valid_suspension_invasion", check_valid_suspension_invasion),
        ("check_judicial_review_required", check_judicial_review_required),
        ("check_criminal_detention_requires_charges", check_criminal_detention_requires_charges),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_HABEAS_CORPUS invariants: PASS")
