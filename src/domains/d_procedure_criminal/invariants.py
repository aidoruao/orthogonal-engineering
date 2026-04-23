#!/usr/bin/env python3
"""Criminal Procedure Invariants.

U.S. Const. amend. IV; Miranda v. Arizona, 384 U.S. 436 (1966);
Speedy Trial Act, 18 U.S.C. § 3161.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Arrest,
    ChargeSeverity,
    CriminalCase,
    Interrogation,
)


def check_probable_cause(arrest: Arrest) -> Tuple[bool, ProofObject]:
    """4th Amendment: Arrest requires probable cause.

    Falsifies if: evidence_weight < Fraction(51, 100).
    falsifies_if: evidence_weight < Fraction(51, 100).
    """
    threshold = Fraction(51, 100)
    strength = arrest.probable_cause_strength()
    if strength < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Arrest without probable cause — strength {strength} < {threshold}",
            premises=[
                f"Evidence weight: {arrest.evidence_weight}",
                f"Probable cause exists: {arrest.probable_cause_exists}",
                f"Threshold: {threshold}",
            ],
            rule="fourth_amendment_pc"
        )
    return True, ProofObject(
        conclusion=f"Probable cause exists — strength {strength} >= {threshold}",
        premises=[f"Strength: {strength}"],
        rule="fourth_amendment_pc"
    )


def check_miranda(interrogation: Interrogation) -> Tuple[bool, ProofObject]:
    """Miranda v. Arizona: Warnings required for custodial interrogation.

    Falsifies if: custodial interrogation occurs with compliance_ratio < 1.
    falsifies_if: custodial interrogation occurs with compliance_ratio < 1.
    """
    ratio = interrogation.miranda_compliance_ratio()
    if ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Custodial interrogation without Miranda compliance — ratio {ratio}",
            premises=[
                f"Custodial: {interrogation.custodial}",
                f"Interrogation: {interrogation.interrogation}",
                f"Miranda given: {interrogation.miranda_given}",
                f"Rights waived: {interrogation.rights_waived}",
                f"Compliance ratio: {ratio}",
            ],
            rule="miranda_warnings"
        )
    return True, ProofObject(
        conclusion=f"Miranda satisfied — compliance ratio {ratio}",
        premises=[f"Compliance ratio: {ratio}"],
        rule="miranda_warnings"
    )


def check_speedy_trial(case: CriminalCase) -> Tuple[bool, ProofObject]:
    """Speedy Trial Act: 70 days from indictment to trial.

    Falsifies if: speedy_trial_ratio > Fraction(1, 1).
    falsifies_if: speedy_trial_ratio > Fraction(1, 1).
    """
    ratio = case.speedy_trial_ratio()
    if ratio > Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Speedy trial right violated — ratio {ratio} > 1",
            premises=[
                f"Indictment date: {case.indictment_date}",
                f"Trial date: {case.trial_date}",
                f"Ratio: {ratio}",
                f"Threshold: 1",
            ],
            rule="speedy_trial_act"
        )
    return True, ProofObject(
        conclusion=f"Speedy trial requirements satisfied — ratio {ratio}",
        premises=[f"Ratio: {ratio}"],
        rule="speedy_trial_act"
    )


def run_all_invariants() -> dict:
    """Run all D_PROCEDURE_CRIMINAL invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    from datetime import datetime

    # Passing data
    pass_arrest = Arrest(
        suspect="Alpha",
        arrest_date=datetime(2025, 1, 1),
        probable_cause_exists=True,
        evidence_weight=Fraction(75, 100),
    )
    pass_interrogation = Interrogation(
        suspect="Alpha",
        custodial=True,
        interrogation=True,
        miranda_given=True,
        rights_waived=True,
    )
    pass_case = CriminalCase(
        case_number="CR-2025-001",
        defendant="Alpha",
        charge="theft",
        severity=ChargeSeverity.MISDEMEANOR,
        arrest_date=datetime(2025, 1, 1),
        indictment_date=datetime(2025, 1, 10),
        trial_date=datetime(2025, 2, 15),
    )

    # Failing data
    fail_arrest = Arrest(
        suspect="Beta",
        arrest_date=datetime(2025, 1, 1),
        probable_cause_exists=False,
        evidence_weight=Fraction(30, 100),
    )
    fail_interrogation = Interrogation(
        suspect="Beta",
        custodial=True,
        interrogation=True,
        miranda_given=False,
        rights_waived=False,
    )
    fail_case = CriminalCase(
        case_number="CR-2025-002",
        defendant="Beta",
        charge="fraud",
        severity=ChargeSeverity.FELONY,
        arrest_date=datetime(2025, 1, 1),
        indictment_date=datetime(2025, 1, 10),
        trial_date=datetime(2025, 5, 1),
    )

    checks = [
        ("check_probable_cause_pass", lambda: check_probable_cause(pass_arrest)),
        ("check_probable_cause_fail", lambda: check_probable_cause(fail_arrest)),
        ("check_miranda_pass", lambda: check_miranda(pass_interrogation)),
        ("check_miranda_fail", lambda: check_miranda(fail_interrogation)),
        ("check_speedy_trial_pass", lambda: check_speedy_trial(pass_case)),
        ("check_speedy_trial_fail", lambda: check_speedy_trial(fail_case)),
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
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_PROCEDURE_CRIMINAL invariants: PASS")
