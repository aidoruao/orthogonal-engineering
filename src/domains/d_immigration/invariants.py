#!/usr/bin/env python3
"""Immigration Law Invariants — INA compliance."""

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

    Falsifies if: applicant fails to meet the requirements for the requested visa category.
    falsifies_if: applicant fails to meet the requirements for the requested visa category.
    """
    if not checker.meets_category_requirements():
        return False, ProofObject(
            conclusion=f"VIOLATION: Applicant does not meet {checker.applicant.visa_category.name} requirements",
            premises=[],
            rule="ina_visa_category"
        )
    
    return True, ProofObject(
        conclusion=f"Visa category requirements satisfied for {checker.applicant.visa_category.name}",
        premises=[],
        rule="ina_visa_category"
    )


def check_processing_deadline(timer: ProcessingTimer) -> Tuple[bool, ProofObject]:
    """INA: Processing must not exceed statutory deadlines.

    Falsifies if: days_elapsed exceeds statutory_deadline_days.
    falsifies_if: days_elapsed exceeds statutory_deadline_days.
    """
    if timer.is_overdue():
        return False, ProofObject(
            conclusion=f"VIOLATION: Processing {timer.days_elapsed} days > deadline {timer.statutory_deadline_days}",
            premises=[],
            rule="ina_processing_deadline"
        )
    
    return True, ProofObject(
        conclusion=f"Processing within deadline ({timer.days_elapsed}/{timer.statutory_deadline_days} days)",
        premises=[],
        rule="ina_processing_deadline"
    )


def check_status_transition(machine: StatusStateMachine) -> Tuple[bool, ProofObject]:
    """Status transitions must follow valid paths.

    Falsifies if: requested_status is not reachable from current_status.
    falsifies_if: requested_status is not reachable from current_status.
    """
    if not machine.is_valid_transition():
        return False, ProofObject(
            conclusion=f"VIOLATION: Invalid transition {machine.current_status} -> {machine.requested_status}",
            premises=[],
            rule="status_transition"
        )
    
    return True, ProofObject(
        conclusion=f"Valid status transition: {machine.current_status} -> {machine.requested_status}",
        premises=[],
        rule="status_transition"
    )


def run_all_invariants() -> dict:
    """Run all D_IMMIGRATION invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    processing_timer = ProcessingTimer(
        application_date="SAMPLE",
        current_date="SAMPLE",
        days_elapsed=1,
    )
    status_state_machine = StatusStateMachine(
        current_status="ACTIVE",
        requested_status="ACTIVE",
    )
    visa_category_checker = VisaCategoryChecker(
        applicant=VisaApplicant(
        applicant_id="IMMIGRAT-001",
        priority_date="SAMPLE",
        visa_category=VisaCategory.EB1,
        country_of_chargeability="SAMPLE",
    ),
    )

    checks = [
        ("check_processing_deadline", lambda: check_processing_deadline(processing_timer)),
        ("check_status_transition", lambda: check_status_transition(status_state_machine)),
        ("check_visa_eligibility", lambda: check_visa_eligibility(visa_category_checker)),
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
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_IMMIGRATION invariants: PASS")
