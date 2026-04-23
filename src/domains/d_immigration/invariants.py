#!/usr/bin/env python3
"""Immigration Law Invariants — INA compliance.

INA § 203(b)(1) (8 U.S.C. § 1153(b)(1)); 8 C.F.R. § 204.5;
Matter of Kazarian, 22 I&N Dec. 717 (BIA 1999).
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    ProcessingTimer,
    StatusStateMachine,
    VisaApplicant,
    VisaCategoryChecker,
    VisaCategory,
)


def check_visa_eligibility(checker: VisaCategoryChecker) -> Tuple[bool, ProofObject]:
    """INA: Visa category requirements must be met.

    Falsifies if: qualification_score < Fraction(7, 10).
    falsifies_if: qualification_score < Fraction(7, 10).
    """
    score = checker.qualification_score()
    threshold = Fraction(7, 10)
    if score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Applicant qualification score {score} < {threshold}",
            premises=[
                f"Category: {checker.applicant.visa_category.name}",
                f"Score: {score}",
                f"Threshold: {threshold}",
            ],
            rule="ina_visa_category"
        )
    return True, ProofObject(
        conclusion=f"Visa category requirements satisfied — score {score}",
        premises=[f"Score: {score}", f"Threshold: {threshold}"],
        rule="ina_visa_category"
    )


def check_processing_deadline(timer: ProcessingTimer) -> Tuple[bool, ProofObject]:
    """INA: Processing must not exceed statutory deadlines.

    Falsifies if: processing_ratio > Fraction(1, 1).
    falsifies_if: processing_ratio > Fraction(1, 1).
    """
    ratio = timer.processing_ratio()
    if ratio > Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Processing ratio {ratio} exceeds 1",
            premises=[
                f"Days elapsed: {timer.days_elapsed}",
                f"Deadline: {timer.statutory_deadline_days}",
                f"Ratio: {ratio}",
            ],
            rule="ina_processing_deadline"
        )
    return True, ProofObject(
        conclusion=f"Processing within deadline — ratio {ratio}",
        premises=[f"Ratio: {ratio}"],
        rule="ina_processing_deadline"
    )


def check_status_transition(machine: StatusStateMachine) -> Tuple[bool, ProofObject]:
    """Status transitions must follow valid paths.

    Falsifies if: transition_validity_score < Fraction(1, 1).
    falsifies_if: transition_validity_score < Fraction(1, 1).
    """
    score = machine.transition_validity_score()
    if score < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Invalid transition {machine.current_status} -> {machine.requested_status}",
            premises=[
                f"Current: {machine.current_status}",
                f"Requested: {machine.requested_status}",
                f"Validity score: {score}",
            ],
            rule="status_transition"
        )
    return True, ProofObject(
        conclusion=f"Valid status transition — score {score}",
        premises=[f"Score: {score}"],
        rule="status_transition"
    )


def run_all_invariants() -> dict:
    """Run all D_IMMIGRATION invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing data
    pass_checker = VisaCategoryChecker(
        applicant=VisaApplicant(
            applicant_id="IMMIG-001",
            priority_date="2024-01-01",
            visa_category=VisaCategory.EB2,
            country_of_chargeability="India",
            education_years=6,
        ),
        required_education_years=5,
    )
    pass_timer = ProcessingTimer(
        application_date="2024-01-01",
        current_date="2024-03-01",
        days_elapsed=60,
        statutory_deadline_days=180,
    )
    pass_machine = StatusStateMachine(
        current_status="F1",
        requested_status="OPT",
    )

    # Failing data
    fail_checker = VisaCategoryChecker(
        applicant=VisaApplicant(
            applicant_id="IMMIG-002",
            priority_date="2024-01-01",
            visa_category=VisaCategory.EB2,
            country_of_chargeability="China",
            education_years=2,
        ),
        required_education_years=5,
    )
    fail_timer = ProcessingTimer(
        application_date="2024-01-01",
        current_date="2024-10-01",
        days_elapsed=200,
        statutory_deadline_days=180,
    )
    fail_machine = StatusStateMachine(
        current_status="F1",
        requested_status="LPR",
    )

    checks = [
        ("check_visa_eligibility_pass", lambda: check_visa_eligibility(pass_checker)),
        ("check_visa_eligibility_fail", lambda: check_visa_eligibility(fail_checker)),
        ("check_processing_deadline_pass", lambda: check_processing_deadline(pass_timer)),
        ("check_processing_deadline_fail", lambda: check_processing_deadline(fail_timer)),
        ("check_status_transition_pass", lambda: check_status_transition(pass_machine)),
        ("check_status_transition_fail", lambda: check_status_transition(fail_machine)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS") and not k.endswith("_fail")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_IMMIGRATION invariants: PASS")
