#!/usr/bin/env python3
"""Criminal Procedure Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Arrest,
    ChargeSeverity,
    CriminalCase,
    Interrogation,
    SPEEDY_TRIAL_DAYS,
)

def check_probable_cause(arrest: Arrest) -> Tuple[bool, ProofObject]:
    """4th Amendment: Arrest requires probable cause.

    Falsifies if: arrest.probable_cause_exists is False.
    falsifies_if: arrest.probable_cause_exists is False.
    """
    if arrest.probable_cause_exists:
        return True, ProofObject(
            conclusion="Probable cause exists — arrest valid",
            premises=[],
            rule="fourth_amendment_pc"
        )
    return False, ProofObject(
        conclusion="VIOLATION: Arrest without probable cause",
        premises=[],
        rule="fourth_amendment_pc"
    )

def check_miranda(interrogation: Interrogation) -> Tuple[bool, ProofObject]:
    """Miranda v. Arizona: Warnings required for custodial interrogation.

    Falsifies if: custodial interrogation occurs without valid Miranda warnings.
    falsifies_if: custodial interrogation occurs without valid Miranda warnings.
    """
    if not interrogation.miranda_required():
        return True, ProofObject(
            conclusion="Miranda not applicable",
            premises=[],
            rule="miranda_applicability"
        )
    
    if interrogation.statement_admissible():
        return True, ProofObject(
            conclusion="Miranda satisfied — statement admissible",
            premises=[],
            rule="miranda_warnings"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Custodial interrogation without Miranda warnings",
        premises=[],
        rule="miranda_warnings"
    )

def check_speedy_trial(case: CriminalCase) -> Tuple[bool, ProofObject]:
    """Speedy Trial Act: 70 days from indictment to trial.

    Falsifies if: speedy_trial_violation returns True.
    falsifies_if: speedy_trial_violation returns True.
    """
    if case.speedy_trial_violation():
        return False, ProofObject(
            conclusion="VIOLATION: Speedy trial right violated",
            premises=[],
            rule="speedy_trial_act"
        )
    return True, ProofObject(
        conclusion="Speedy trial requirements satisfied",
        premises=[],
        rule="speedy_trial_act"
    )


def run_all_invariants() -> dict:
    """Run all D_PROCEDURE_CRIMINAL invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    interrogation = Interrogation(
        suspect="SAMPLE",
    )
    arrest = Arrest(
        suspect="SAMPLE",
        arrest_date=None,
    )
    criminal_case = CriminalCase(
        case_number="SAMPLE",
        defendant="SAMPLE",
        charge="SAMPLE",
        severity=ChargeSeverity.MISDEMEANOR,
        arrest_date=None,
    )

    checks = [
        ("check_miranda", lambda: check_miranda(interrogation)),
        ("check_probable_cause", lambda: check_probable_cause(arrest)),
        ("check_speedy_trial", lambda: check_speedy_trial(criminal_case)),
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
    print("All D_PROCEDURE_CRIMINAL invariants: PASS")
