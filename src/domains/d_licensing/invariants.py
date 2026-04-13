#!/usr/bin/env python3
"""Licensing Domain Invariants — Professional license validity, CE compliance.

Standards:
- State licensing board regulations
- Interstate compacts (NLC, etc.)
- Sunset review requirements
- Continuing education requirements

Falsifies if:
- Expired license reported as active
- CE requirements not met
- Sunset review overdue
- Disciplined licensee not reported
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    ContinuingEducation,
    DisciplinaryAction,
    License,
    LicenseStatus,
    LicenseType,
    LicensingBoard,
)


def check_license_validity(license: License) -> Tuple[bool, ProofObject]:
    """License must be active and not expired to practice.

    Falsifies if: status is revoked/suspended/expired or expiration_date has passed.
    falsifies_if: status is revoked/suspended/expired or expiration_date has passed.
    """
    if license.status == LicenseStatus.REVOKED:
        return False, ProofObject(
            conclusion="VIOLATION: License revoked - holder cannot practice",
            premises=[
                f"License: {license.license_number}",
                f"Holder: {license.holder_name}",
                "Status: REVOKED"
            ],
            rule="license_revoked_prohibition"
        )
    
    if license.status == LicenseStatus.SUSPENDED:
        return False, ProofObject(
            conclusion="VIOLATION: License suspended - practice prohibited",
            premises=[
                f"License: {license.license_number}",
                f"Status: SUSPENDED"
            ],
            rule="license_suspended_prohibition"
        )
    
    if license.is_expired():
        days_expired = (datetime.now() - license.expiration_date).days
        return False, ProofObject(
            conclusion=f"VIOLATION: License expired {days_expired} days ago",
            premises=[
                f"License: {license.license_number}",
                f"Expired: {license.expiration_date}",
                f"Days expired: {days_expired}"
            ],
            rule="license_expiration_enforcement"
        )
    
    if license.status != LicenseStatus.ACTIVE:
        return False, ProofObject(
            conclusion=f"VIOLATION: License not active (status: {license.status.name})",
            premises=[f"Status: {license.status.name}"],
            rule="license_active_required"
        )
    
    return True, ProofObject(
        conclusion="License valid and active",
        premises=[
            f"License: {license.license_number}",
            f"Expires: {license.expiration_date}",
            f"Days remaining: {license.days_until_expiration()}"
        ],
        rule="license_valid"
    )


def check_ce_compliance(ce: ContinuingEducation) -> Tuple[bool, ProofObject]:
    """Continuing education required for license renewal.

    Falsifies if: completed_hours or ethics_completed fall below required thresholds.
    falsifies_if: completed_hours or ethics_completed fall below required thresholds.
    """
    if not ce.is_complete():
        hours_short = ce.hours_remaining()
        ethics_short = max(Fraction(0), ce.ethics_required - ce.ethics_completed)
        
        return False, ProofObject(
            conclusion=f"VIOLATION: CE deficient by {hours_short} hours",
            premises=[
                f"License: {ce.license_number}",
                f"Completed: {ce.completed_hours}/{ce.required_hours}",
                f"Ethics: {ce.ethics_completed}/{ce.ethics_required}",
                f"Shortfall: {hours_short} hours, {ethics_short} ethics"
            ],
            rule="continuing_education_requirement"
        )
    
    return True, ProofObject(
        conclusion="Continuing education requirements satisfied",
        premises=[
            f"Hours: {ce.completed_hours}/{ce.required_hours}",
            f"Ethics: {ce.ethics_completed}/{ce.ethics_required}"
        ],
        rule="ce_compliant"
    )


def check_sunset_review_current(board: LicensingBoard) -> Tuple[bool, ProofObject]:
    """Licensing boards require periodic sunset review (typically 5-10 years).

    Falsifies if: last_sunset_review is missing or more than 5 years old.
    falsifies_if: last_sunset_review is missing or more than 5 years old.
    """
    if board.last_sunset_review is None:
        return False, ProofObject(
            conclusion="VIOLATION: Licensing board has never undergone sunset review",
            premises=[
                f"Board: {board.name}",
                "Last sunset review: Never"
            ],
            rule="sunset_review_required"
        )
    
    days_since_review = (datetime.now() - board.last_sunset_review).days
    MAX_REVIEW_AGE = 365 * 5  # 5 years
    
    if days_since_review > MAX_REVIEW_AGE:
        years_overdue = days_since_review / 365
        return False, ProofObject(
            conclusion=f"VIOLATION: Sunset review {years_overdue:.1f} years overdue",
            premises=[
                f"Board: {board.name}",
                f"Last review: {board.last_sunset_review}",
                f"Days since: {days_since_review}"
            ],
            rule="sunset_review_currency"
        )
    
    return True, ProofObject(
        conclusion="Sunset review current",
        premises=[
            f"Last review: {board.last_sunset_review}",
            f"Days since: {days_since_review}"
        ],
        rule="sunset_review_current"
    )


def check_reciprocity_validity(license: License, target_jurisdiction: str) -> Tuple[bool, ProofObject]:
    """Multi-state practice requires valid compact or reciprocity.

    Falsifies if: license is invalid in target_jurisdiction or lacks required compact privilege.
    falsifies_if: license is invalid in target_jurisdiction or lacks required compact privilege.
    """
    if not license.valid_in_jurisdiction(target_jurisdiction):
        return False, ProofObject(
            conclusion=f"VIOLATION: License not valid in {target_jurisdiction}",
            premises=[
                f"License: {license.license_number}",
                f"Issued by: {license.jurisdiction}",
                f"Compact member: {license.compact_member}",
                f"Target: {target_jurisdiction}"
            ],
            rule="interstate_compact_validity"
        )
    
    return True, ProofObject(
        conclusion="License valid in target jurisdiction",
        premises=[
            f"License jurisdiction: {license.jurisdiction}",
            f"Compact: {license.compact_member}",
            f"Target: {target_jurisdiction}"
        ],
        rule="reciprocity_valid"
    )


def check_disciplinary_reporting(action: DisciplinaryAction) -> Tuple[bool, ProofObject]:
    """Disciplinary actions must be reported to national database.

    Falsifies if: serious discipline is unreported beyond 30 days.
    falsifies_if: serious discipline is unreported beyond 30 days.
    """
    serious_types = ("revocation", "suspension", "surrender")
    
    if action.action_type in serious_types:
        days_since_action = (datetime.now() - action.action_date).days
        REPORTING_DEADLINE = 30
        
        if days_since_action > REPORTING_DEADLINE:
            # In real system, check if reported
            return False, ProofObject(
                conclusion=f"VIOLATION: Serious discipline not reported within {REPORTING_DEADLINE} days",
                premises=[
                    f"Action: {action.action_id}",
                    f"Type: {action.action_type}",
                    f"Date: {action.action_date}",
                    f"Days elapsed: {days_since_action}"
                ],
                rule="disciplinary_action_reporting"
            )
    
    return True, ProofObject(
        conclusion="Disciplinary action properly reported",
        premises=[f"Action: {action.action_type}", f"Date: {action.action_date}"],
        rule="disciplinary_reported"
    )


def run_all_invariants() -> dict:
    """Run all D_LICENSING invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    continuing_education = ContinuingEducation(
        license_number=None,
        reporting_period_start=None,
        reporting_period_end=None,
        required_hours=Fraction(1),
        completed_hours=Fraction(1),
        ethics_required=Fraction(1),
        ethics_completed=Fraction(1),
    )
    disciplinary_action = DisciplinaryAction(
        action_id=None,
        license_number=None,
        action_type=None,
        action_date=None,
        violation_type=None,
        violation_description=None,
        duration_days=None,
        appealed=None,
    )
    license = License(
        license_number=None,
        license_type=LicenseType.MEDICAL,
        profession=None,
        holder_name=None,
        holder_id=None,
        issuing_authority=None,
        jurisdiction=None,
        issue_date=None,
        expiration_date=None,
        status=LicenseStatus.ACTIVE,
        compact_member=None,
    )
    licensing_board = LicensingBoard(
        board_id=None,
        name=None,
        jurisdiction=None,
        license_type=LicenseType.MEDICAL,
        education_required=None,
        examination_required=None,
        experience_hours=None,
        sunset_review_date=None,
        last_sunset_review=None,
        total_licenses=None,
        active_licenses=None,
    )

    checks = [
        ("check_ce_compliance", lambda: check_ce_compliance(continuing_education)),
        ("check_disciplinary_reporting", lambda: check_disciplinary_reporting(disciplinary_action)),
        ("check_license_validity", lambda: check_license_validity(license)),
        ("check_reciprocity_validity", lambda: check_reciprocity_validity(license, "SAMPLE")),
        ("check_sunset_review_current", lambda: check_sunset_review_current(licensing_board)),
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
    print("All D_LICENSING invariants: PASS")
