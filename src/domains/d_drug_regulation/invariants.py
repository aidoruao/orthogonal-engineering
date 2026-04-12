"""D_DRUG_REGULATION invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes FDA and DEA
drug regulatory requirements.

Standards:
- FD&C Act §505 (21 U.S.C. §355)
- Controlled Substances Act (CSA, 21 U.S.C. §801)
- DEA Regulations (21 CFR Part 1306)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import DrugApplication


def check_nda_approval_required(app: DrugApplication) -> Tuple[bool, ProofObject]:
    """
    Rule: A drug must have an approved NDA or ANDA before marketing (FD&C Act §505).

    falsifies_if: neither nda_approved nor anda_approved is True.
    """
    success = app.nda_approved or app.anda_approved

    if not success:
        return False, ProofObject(
            rule="NDAApprovalRequired",
            premises=[
                f"drug_id={app.drug_id}",
                f"nda_approved={app.nda_approved}",
                f"anda_approved={app.anda_approved}",
                f"generic_drug={app.generic_drug}",
            ],
            conclusion="VIOLATION: FD&C Act §505 — drug marketed without NDA or ANDA approval",
        )

    return True, ProofObject(
        rule="NDAApprovalRequired",
        premises=[
            f"drug_id={app.drug_id}",
            f"nda_approved={app.nda_approved}",
            f"anda_approved={app.anda_approved}",
        ],
        conclusion="FD&C Act §505 marketing authorization satisfied",
    )


def check_controlled_substance_registration(app: DrugApplication) -> Tuple[bool, ProofObject]:
    """
    Rule: Schedule II-V controlled substances require DEA registration to handle (CSA 21 U.S.C. §822).

    falsifies_if: schedule in {"II","III","IV","V"} AND dea_registration is False.
    """
    controlled_schedules = {"I", "II", "III", "IV", "V"}
    requires_dea = app.schedule in controlled_schedules
    success = not requires_dea or app.dea_registration

    if not success:
        return False, ProofObject(
            rule="ControlledSubstanceDEARegistration",
            premises=[
                f"drug_id={app.drug_id}",
                f"schedule={app.schedule}",
                f"dea_registration={app.dea_registration}",
            ],
            conclusion=f"VIOLATION: CSA §822 — Schedule {app.schedule} substance handled without DEA registration",
        )

    return True, ProofObject(
        rule="ControlledSubstanceDEARegistration",
        premises=[
            f"drug_id={app.drug_id}",
            f"schedule={app.schedule}",
            f"dea_registration={app.dea_registration}",
        ],
        conclusion="CSA §822 DEA registration requirement satisfied",
    )


def check_prescription_requirement(app: DrugApplication) -> Tuple[bool, ProofObject]:
    """
    Rule: Prescription-only drugs must complete Phase 3 clinical trials before approval (21 CFR 314).

    falsifies_if: prescription_required is True AND phase3_completed is False AND (nda_approved OR anda_approved).
    """
    if app.prescription_required and (app.nda_approved or app.anda_approved):
        success = app.phase3_completed
    else:
        success = True

    if not success:
        return False, ProofObject(
            rule="PrescriptionDrugClinicalTrials",
            premises=[
                f"drug_id={app.drug_id}",
                f"prescription_required={app.prescription_required}",
                f"phase3_completed={app.phase3_completed}",
                f"nda_approved={app.nda_approved}",
            ],
            conclusion="VIOLATION: 21 CFR 314 — prescription drug approved without completed Phase 3 trials",
        )

    return True, ProofObject(
        rule="PrescriptionDrugClinicalTrials",
        premises=[
            f"drug_id={app.drug_id}",
            f"prescription_required={app.prescription_required}",
            f"phase3_completed={app.phase3_completed}",
        ],
        conclusion="21 CFR 314 prescription drug clinical trial requirement satisfied",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_DRUG_REGULATION invariants with nominal passing data.

    falsifies_if: any drug regulation invariant check fails or raises an exception.
    """
    app = DrugApplication(
        drug_id="DRUG-001",
        nda_approved=True,
        anda_approved=False,
        generic_drug=False,
        schedule="uncontrolled",
        prescription_required=True,
        dea_registration=False,
        clinical_trials_completed=True,
        phase3_completed=True,
    )

    checks = [
        ("check_nda_approval_required", lambda: check_nda_approval_required(app)),
        ("check_controlled_substance_registration", lambda: check_controlled_substance_registration(app)),
        ("check_prescription_requirement", lambda: check_prescription_requirement(app)),
    ]

    results: Dict[str, str] = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_DRUG_REGULATION invariants: PASS")
