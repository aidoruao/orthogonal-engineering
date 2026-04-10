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
