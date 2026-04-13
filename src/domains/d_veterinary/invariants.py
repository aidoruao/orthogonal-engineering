"""D_VETERINARY invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes AWA/USDA animal welfare,
veterinary licensing, FDA CVM drug withdrawal, zoonotic reporting, and AVMA euthanasia
compliance requirements.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    AnimalFacility,
    VeterinaryLicense,
    AnimalTreatment,
    ZoonoticReport,
    EuthanasiaRecord,
)


def check_facility_space_compliance(facility: AnimalFacility) -> Tuple[bool, ProofObject]:
    """
    Rule: Animal housing must provide at minimum the required floor space per animal (AWA 7 U.S.C. §2131, 9 CFR Part 3).

    falsifies_if: space_per_animal_sqft < min_space_sqft.
    """
    compliant = facility.space_per_animal_sqft >= facility.min_space_sqft

    if not compliant:
        return False, ProofObject(
            rule="facility_space_compliance",
            premises=[
                f"facility_id={facility.facility_id}",
                f"space_per_animal_sqft={facility.space_per_animal_sqft}",
                f"min_space_sqft={facility.min_space_sqft}",
            ],
            conclusion="VIOLATION: Facility provides insufficient space per animal under AWA 9 CFR Part 3",
        )

    return True, ProofObject(
        rule="facility_space_compliance",
        premises=[
            f"facility_id={facility.facility_id}",
            f"space_per_animal_sqft={facility.space_per_animal_sqft}",
            f"min_space_sqft={facility.min_space_sqft}",
        ],
        conclusion="Facility space per animal meets AWA/9 CFR Part 3 minimum requirement",
    )


def check_veterinary_license_valid(license: VeterinaryLicense) -> Tuple[bool, ProofObject]:
    """
    Rule: Veterinary license must be active, unexpired, and satisfy continuing education requirements
    (Veterinary Practice Act, state licensing board).

    falsifies_if: license_active is False OR days_until_expiry <= Fraction(0) OR ce_hours_completed < ce_hours_required.
    """
    active = license.license_active
    not_expired = license.days_until_expiry > Fraction(0)
    ce_met = license.ce_hours_completed >= license.ce_hours_required

    if not (active and not_expired and ce_met):
        return False, ProofObject(
            rule="veterinary_license_valid",
            premises=[
                f"vet_id={license.vet_id}",
                f"state={license.state}",
                f"license_active={license.license_active}",
                f"days_until_expiry={license.days_until_expiry}",
                f"ce_hours_completed={license.ce_hours_completed}",
                f"ce_hours_required={license.ce_hours_required}",
            ],
            conclusion="VIOLATION: Veterinary license inactive, expired, or CE hours deficient",
        )

    return True, ProofObject(
        rule="veterinary_license_valid",
        premises=[
            f"vet_id={license.vet_id}",
            f"state={license.state}",
            "license_active=True",
            f"days_until_expiry={license.days_until_expiry}",
            f"ce_hours_completed={license.ce_hours_completed}",
            f"ce_hours_required={license.ce_hours_required}",
        ],
        conclusion="Veterinary license active, unexpired, and CE requirements met",
    )


def check_drug_withdrawal_period(treatment: AnimalTreatment) -> Tuple[bool, ProofObject]:
    """
    Rule: Drugs administered to animals must be FDA-CVM approved and the withdrawal period must
    be fully observed before the animal enters the food supply (FDA CVM, 21 CFR).

    falsifies_if: fda_cvm_approved is False OR days_since_treatment < withdrawal_period_days.
    """
    approved = treatment.fda_cvm_approved
    withdrawal_observed = treatment.days_since_treatment >= treatment.withdrawal_period_days

    if not (approved and withdrawal_observed):
        return False, ProofObject(
            rule="drug_withdrawal_period",
            premises=[
                f"treatment_id={treatment.treatment_id}",
                f"drug_administered={treatment.drug_administered}",
                f"fda_cvm_approved={treatment.fda_cvm_approved}",
                f"days_since_treatment={treatment.days_since_treatment}",
                f"withdrawal_period_days={treatment.withdrawal_period_days}",
            ],
            conclusion="VIOLATION: Drug not FDA-CVM approved or withdrawal period not elapsed per 21 CFR",
        )

    return True, ProofObject(
        rule="drug_withdrawal_period",
        premises=[
            f"treatment_id={treatment.treatment_id}",
            f"drug_administered={treatment.drug_administered}",
            "fda_cvm_approved=True",
            f"days_since_treatment={treatment.days_since_treatment}",
            f"withdrawal_period_days={treatment.withdrawal_period_days}",
        ],
        conclusion="Drug is FDA-CVM approved and withdrawal period fully observed per 21 CFR",
    )


def check_zoonotic_disease_reporting(report: ZoonoticReport) -> Tuple[bool, ProofObject]:
    """
    Rule: Reportable zoonotic diseases must be reported to competent authorities within the maximum
    permitted time window (OIE Terrestrial Code, applicable state regulations).

    falsifies_if: reportable is True AND reported_within_hours > max_reporting_hours.
    """
    if not report.reportable:
        return True, ProofObject(
            rule="zoonotic_disease_reporting",
            premises=[
                f"report_id={report.report_id}",
                f"disease_name={report.disease_name}",
                "reportable=False",
            ],
            conclusion="Disease is not reportable; no reporting obligation applies",
        )

    timely = report.reported_within_hours <= report.max_reporting_hours

    if not timely:
        return False, ProofObject(
            rule="zoonotic_disease_reporting",
            premises=[
                f"report_id={report.report_id}",
                f"disease_name={report.disease_name}",
                "reportable=True",
                f"reported_within_hours={report.reported_within_hours}",
                f"max_reporting_hours={report.max_reporting_hours}",
            ],
            conclusion="VIOLATION: Reportable zoonotic disease not reported within required time window per OIE/state regulations",
        )

    return True, ProofObject(
        rule="zoonotic_disease_reporting",
        premises=[
            f"report_id={report.report_id}",
            f"disease_name={report.disease_name}",
            "reportable=True",
            f"reported_within_hours={report.reported_within_hours}",
            f"max_reporting_hours={report.max_reporting_hours}",
        ],
        conclusion="Zoonotic disease reported within required window per OIE Terrestrial Code",
    )


def check_euthanasia_compliance(record: EuthanasiaRecord) -> Tuple[bool, ProofObject]:
    """
    Rule: Euthanasia must use an AVMA-approved method, be performed by or under a licensed
    veterinarian, and minimize pain (AVMA Guidelines for the Euthanasia of Animals).

    falsifies_if: avma_approved is False OR veterinarian_present is False OR pain_minimized is False.
    """
    method_approved = record.avma_approved
    vet_present = record.veterinarian_present
    pain_controlled = record.pain_minimized

    if not (method_approved and vet_present and pain_controlled):
        return False, ProofObject(
            rule="euthanasia_compliance",
            premises=[
                f"record_id={record.record_id}",
                f"method={record.method}",
                f"avma_approved={record.avma_approved}",
                f"veterinarian_present={record.veterinarian_present}",
                f"pain_minimized={record.pain_minimized}",
            ],
            conclusion="VIOLATION: Euthanasia method not AVMA-approved, veterinarian absent, or pain not minimized",
        )

    return True, ProofObject(
        rule="euthanasia_compliance",
        premises=[
            f"record_id={record.record_id}",
            f"method={record.method}",
            "avma_approved=True",
            "veterinarian_present=True",
            "pain_minimized=True",
        ],
        conclusion="Euthanasia compliant with AVMA Guidelines: approved method, veterinarian present, pain minimized",
    )


def check_inspection_currency(facility: AnimalFacility) -> Tuple[bool, ProofObject]:
    """
    Rule: Regulated animal facilities must be inspected within the USDA APHIS-mandated interval
    (USDA APHIS, 9 CFR Part 2).

    falsifies_if: last_inspection_days_ago > max_inspection_interval_days.
    """
    current = facility.last_inspection_days_ago <= facility.max_inspection_interval_days

    if not current:
        return False, ProofObject(
            rule="inspection_currency",
            premises=[
                f"facility_id={facility.facility_id}",
                f"last_inspection_days_ago={facility.last_inspection_days_ago}",
                f"max_inspection_interval_days={facility.max_inspection_interval_days}",
            ],
            conclusion="VIOLATION: Facility inspection overdue per USDA APHIS 9 CFR Part 2",
        )

    return True, ProofObject(
        rule="inspection_currency",
        premises=[
            f"facility_id={facility.facility_id}",
            f"last_inspection_days_ago={facility.last_inspection_days_ago}",
            f"max_inspection_interval_days={facility.max_inspection_interval_days}",
        ],
        conclusion="Facility inspection is current per USDA APHIS 9 CFR Part 2",
    )


def run_all_invariants() -> dict:
    """Run all D_VETERINARY invariants with nominal sample data.

    Falsifies if: any veterinary invariant fails or raises an exception.
    falsifies_if: any veterinary invariant fails or raises an exception.
    """
    facility = AnimalFacility(
        facility_id="FAC-001",
        license_number="LIC-98765",
        space_per_animal_sqft=Fraction(50),
        min_space_sqft=Fraction(25),
        veterinarian_on_call=True,
        last_inspection_days_ago=Fraction(180),
        max_inspection_interval_days=Fraction(365),
    )
    license_ = VeterinaryLicense(
        vet_id="VET-001",
        state="TX",
        license_active=True,
        days_until_expiry=Fraction(365),
        dea_registration=True,
        ce_hours_completed=Fraction(30),
        ce_hours_required=Fraction(20),
    )
    treatment = AnimalTreatment(
        treatment_id="TRT-001",
        animal_id="ANIMAL-001",
        drug_administered="penicillin",
        fda_cvm_approved=True,
        withdrawal_period_days=Fraction(7),
        days_since_treatment=Fraction(10),
        extra_label_use=False,
        veterinarian_supervised=True,
    )
    report = ZoonoticReport(
        report_id="ZOO-001",
        disease_name="brucellosis",
        reportable=True,
        reported_within_hours=Fraction(12),
        max_reporting_hours=Fraction(24),
        species_affected="bovine",
    )
    euthanasia = EuthanasiaRecord(
        record_id="EUT-001",
        method="pentobarbital-IV",
        avma_approved=True,
        veterinarian_present=True,
        pain_minimized=True,
    )

    checks = [
        ("check_facility_space_compliance", lambda: check_facility_space_compliance(facility)),
        ("check_veterinary_license_valid", lambda: check_veterinary_license_valid(license_)),
        ("check_drug_withdrawal_period", lambda: check_drug_withdrawal_period(treatment)),
        ("check_zoonotic_disease_reporting", lambda: check_zoonotic_disease_reporting(report)),
        ("check_euthanasia_compliance", lambda: check_euthanasia_compliance(euthanasia)),
        ("check_inspection_currency", lambda: check_inspection_currency(facility)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_VETERINARY invariants: PASS")
