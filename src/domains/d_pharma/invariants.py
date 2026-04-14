#!/usr/bin/env python3
"""Pharma Domain Invariants — FDA compliance, GMP, clinical trials.

Standards:
- 21 CFR
- ICH-GCP
- FD&C Act
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Drug, ClinicalTrial, AdverseEvent


def check_fda_approved(drug: Drug) -> Tuple[bool, ProofObject]:
    """Drug must be FDA approved before marketing.

    Falsifies if: drug.is_approved() returns False.
    falsifies_if: drug.is_approved() returns False.
    """
    if not drug.is_approved():
        return False, ProofObject(
            conclusion="VIOLATION: Unapproved drug in commerce",
            premises=[f"Drug: {drug.ndc}"],
            rule="fdca_unapproved_drugs"
        )
    return True, ProofObject(
        conclusion="Drug FDA approved",
        premises=[],
        rule="approval_compliant"
    )


def check_gmp_compliance(drug: Drug) -> Tuple[bool, ProofObject]:
    """Manufacturing must comply with GMP certification.

    Falsifies if: gmp_certified is False.
    falsifies_if: gmp_certified is False.
    """
    if not drug.gmp_certified:
        return False, ProofObject(
            conclusion="VIOLATION: GMP certification missing",
            premises=[f"Drug: {drug.ndc}"],
            rule="21_cfr_210_211_gmp"
        )
    return True, ProofObject(
        conclusion="GMP compliant",
        premises=[],
        rule="gmp_compliant"
    )


def check_ind_status(trial: ClinicalTrial) -> Tuple[bool, ProofObject]:
    """Clinical trials require active IND through Phase 3.

    Falsifies if: phase < 4 and ind_active is False.
    falsifies_if: phase < 4 and ind_active is False.
    """
    if trial.phase < 4 and not trial.ind_active:
        return False, ProofObject(
            conclusion="VIOLATION: Clinical trial without active IND",
            premises=[f"Trial: {trial.nct_number}"],
            rule="21_cfr_312_ind"
        )
    return True, ProofObject(
        conclusion="IND active",
        premises=[],
        rule="ind_compliant"
    )


def check_ae_reporting(event: AdverseEvent) -> Tuple[bool, ProofObject]:
    """Serious adverse events must be reported within regulatory timelines.

    Falsifies if: reported_timely returns False.
    falsifies_if: reported_timely returns False.
    """
    if not event.reported_timely():
        days = (event.fda_received - event.report_date).days
        limit = 15 if event.serious else 90
        return False, ProofObject(
            conclusion=f"VIOLATION: AE report {days} days late (limit {limit})",
            premises=[f"Report: {event.report_id}"],
            rule="21_cfr_312_32_ae_reporting"
        )
    return True, ProofObject(
        conclusion="AE reported timely",
        premises=[],
        rule="ae_compliant"
    )


def check_recall_status(drug: Drug) -> Tuple[bool, ProofObject]:
    """Recalls must halt distribution.

    Falsifies if: recall_status indicates an active recall.
    falsifies_if: recall_status indicates an active recall.
    """
    if drug.recall_status:
        return False, ProofObject(
            conclusion="WARNING: Drug subject to recall",
            premises=[f"Drug: {drug.ndc}"],
            rule="fda_recall"
        )
    return True, ProofObject(
        conclusion="No active recall",
        premises=[],
        rule="recall_compliant"
    )


def check_trial_enrollment(trial: ClinicalTrial) -> Tuple[bool, ProofObject]:
    """Clinical trials must sustain adequate enrollment/retention.

    Falsifies if: enrollment_rate falls below the threshold (0.8).
    falsifies_if: enrollment_rate falls below the threshold (0.8).
    """
    rate = trial.enrollment_rate()
    if rate < Fraction(8, 10):
        return False, ProofObject(
            conclusion=f"WARNING: Trial completion rate {rate} below threshold",
            premises=[],
            rule="trial_retention"
        )
    return True, ProofObject(
        conclusion="Trial completion acceptable",
        premises=[f"Rate: {rate}"],
        rule="enrollment_compliant"
    )


def run_all_invariants() -> dict:
    """Run all D_PHARMA invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    adverse_event = AdverseEvent(
        report_id=None,
        drug_ndc=None,
        serious=None,
        death=None,
        report_date=None,
        fda_received=None,
    )
    drug = Drug(
        ndc=None,
        name=None,
        manufacturer=None,
        approval_date=None,
        approval_type=None,
        gmp_certified=None,
        recall_status=None,
    )
    clinical_trial = ClinicalTrial(
        nct_number=None,
        phase=None,
        enrolled=None,
        completed=None,
        ind_active=None,
        primary_completion=None,
    )

    checks = [
        ("check_ae_reporting", lambda: check_ae_reporting(adverse_event)),
        ("check_fda_approved", lambda: check_fda_approved(drug)),
        ("check_gmp_compliance", lambda: check_gmp_compliance(drug)),
        ("check_ind_status", lambda: check_ind_status(clinical_trial)),
        ("check_recall_status", lambda: check_recall_status(drug)),
        ("check_trial_enrollment", lambda: check_trial_enrollment(clinical_trial)),
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
    print("All D_PHARMA invariants: PASS")
