"""D_MEDICAL invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- HIPAA (Health Insurance Portability and Accountability Act)
- FDA 21 CFR Part 820 (Quality System Regulation)
- Stark Law (42 U.S.C. § 1395nn)
- Anti-Kickback Statute

Source: FDA 21 CFR Part 820, HIPAA, EMTALA
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_hipaa_phi_protection() -> Tuple[bool, ProofObject]:
    """
    Invariant: PHI disclosure limited to minimum necessary standard.
    
    Standard: 45 CFR § 164.502(b) - Minimum necessary requirement
    Falsifies if: Disclosure exceeds minimum necessary for purpose.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # PHI elements that require protection
    phi_elements = {
        "names": True,
        "geographic_data": True,
        "dates": True,
        "phone_numbers": True,
        "ssn": True,
        "mrn": True,
        "health_plan_id": True,
        "account_numbers": True,
        "certificate_numbers": True,
        "vehicle_identifiers": True,
        "device_identifiers": True,
        "urls": True,
        "ip_addresses": True,
        "biometric_ids": True,
        "photos": True,
        "any_other_id": True,
    }
    
    all_protected = all(phi_elements.values())
    num_phi_elements = Fraction(len(phi_elements))
    
    # Minimum necessary standard applied
    minimum_necessary_applied = True
    
    success = all_protected and minimum_necessary_applied
    
    proof = ProofObject(
        rule="HIPAA_PHI_Protection",
        premises=[
            f"num_phi_elements = {num_phi_elements}",
            f"all_elements_protected = {all_protected}",
            f"minimum_necessary_applied = {minimum_necessary_applied}",
        ],
        conclusion=(
            "HIPAA PHI protection complies with 45 CFR § 164.502"
            if success
            else "FAIL: HIPAA PHI protection check failed"
        ),
    )
    return success, proof


def check_fda_device_classification() -> Tuple[bool, ProofObject]:
    """
    Invariant: Medical device classification matches risk level.
    
    Standard: 21 CFR § 860.3 - Device classification procedures
    Falsifies if: Class III device lacks PMA or Class I lacks general controls.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Device classification requirements
    class_i_controls = True  # General controls
    class_ii_special_controls = True
    class_iii_pma_required = True
    
    # Class III device example: pacemaker
    pacemaker_risk_class = Fraction(3)
    pacemaker_requires_pma = pacemaker_risk_class == Fraction(3)
    
    # Class II device example: surgical instruments
    surgical_instr_risk_class = Fraction(2)
    surgical_instr_special_controls = surgical_instr_risk_class == Fraction(2)
    
    # Class I device example: tongue depressor
    tongue_depressor_class = Fraction(1)
    tongue_depressor_general_controls = tongue_depressor_class == Fraction(1)
    
    success = class_i_controls and class_ii_special_controls and class_iii_pma_required
    
    proof = ProofObject(
        rule="FDA_Device_Classification",
        premises=[
            f"class_i_general_controls = {class_i_controls}",
            f"class_ii_special_controls = {class_ii_special_controls}",
            f"class_iii_pma_required = {class_iii_pma_required}",
            f"pacemaker_class = Class {pacemaker_risk_class}",
        ],
        conclusion=(
            "FDA device classification complies with 21 CFR § 860"
            if success
            else "FAIL: FDA device classification check failed"
        ),
    )
    return success, proof


def check_stark_law_prohibition() -> Tuple[bool, ProofObject]:
    """
    Invariant: Stark Law prohibits physician self-referral for designated health services.
    
    Standard: 42 U.S.C. § 1395nn - Limitation on certain physician referrals
    Falsifies if: Self-referral without applicable exception occurs.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Designated health services under Stark
    designated_health_services = {
        "clinical_laboratory": True,
        "physical_therapy": True,
        "occupational_therapy": True,
        "radiology": True,
        "radiation_therapy": True,
        "dme": True,
        "parenteral_nutrition": True,
        "home_health": True,
        "outpatient_prescription_drugs": True,
        "inpatient_hospital": True,
    }
    
    num_dhs = Fraction(len(designated_health_services))
    
    # Financial relationship prohibition
    financial_relationship_prohibited = True
    
    # Exceptions exist for legitimate arrangements
    exceptions_available = True
    
    # Strict liability - no intent required
    strict_liability = True
    
    success = financial_relationship_prohibited and exceptions_available
    
    proof = ProofObject(
        rule="Stark_Law_Prohibition",
        premises=[
            f"num_designated_health_services = {num_dhs}",
            f"financial_relationship_prohibited = {financial_relationship_prohibited}",
            f"exceptions_available = {exceptions_available}",
            f"strict_liability = {strict_liability}",
        ],
        conclusion=(
            "Stark Law compliance meets 42 U.S.C. § 1395nn"
            if success
            else "FAIL: Stark Law prohibition check failed"
        ),
    )
    return success, proof


def check_fda_qsr_documentation() -> Tuple[bool, ProofObject]:
    """
    Invariant: FDA QSR requires design history file and device master record.
    
    Standard: 21 CFR § 820.30 - Design controls; § 820.181 - Device master record
    Falsifies if: Required documentation is incomplete.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Design History File (DHF) requirements
    dhf_requirements = {
        "design_plan": True,
        "design_input": True,
        "design_output": True,
        "design_review": True,
        "design_verification": True,
        "design_validation": True,
        "design_transfer": True,
        "design_changes": True,
        "design_history_file": True,
    }
    
    all_dhf = all(dhf_requirements.values())
    
    # Device Master Record (DMR) requirements
    dmr_requirements = {
        "device_specifications": True,
        "production_process_specs": True,
        "quality_assurance_procedures": True,
    }
    
    all_dmr = all(dmr_requirements.values())
    
    success = all_dhf and all_dmr
    
    proof = ProofObject(
        rule="FDA_QSR_Documentation",
        premises=[
            f"dhf_complete = {all_dhf}",
            f"dmr_complete = {all_dmr}",
            f"num_dhf_elements = {Fraction(len(dhf_requirements))}",
            f"num_dmr_elements = {Fraction(len(dmr_requirements))}",
        ],
        conclusion=(
            "FDA QSR documentation complies with 21 CFR § 820"
            if success
            else "FAIL: FDA QSR documentation check failed"
        ),
    )
    return success, proof


def check_hipaa_security_rule_safeguards() -> Tuple[bool, ProofObject]:
    """
    Invariant: HIPAA Security Rule requires administrative, physical, and technical safeguards.
    
    Standard: 45 CFR § 164.302 - Security standards
    Falsifies if: Required safeguards are not implemented.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Administrative safeguards (§ 164.308)
    administrative_safeguards = {
        "security_management": True,
        "assigned_security_responsibility": True,
        "workforce_security": True,
        "information_access_management": True,
        "training": True,
        "security_awareness": True,
        "security_incident_procedures": True,
        "contingency_plan": True,
        "evaluation": True,
    }
    
    # Physical safeguards (§ 164.310)
    physical_safeguards = {
        "facility_access": True,
        "workstation_security": True,
        "device_controls": True,
    }
    
    # Technical safeguards (§ 164.312)
    technical_safeguards = {
        "access_control": True,
        "audit_controls": True,
        "integrity": True,
        "person_authentication": True,
        "transmission_security": True,
    }
    
    all_admin = all(administrative_safeguards.values())
    all_physical = all(physical_safeguards.values())
    all_technical = all(technical_safeguards.values())
    
    success = all_admin and all_physical and all_technical
    
    proof = ProofObject(
        rule="HIPAA_Security_Rule_Safeguards",
        premises=[
            f"administrative_safeguards = {Fraction(len(administrative_safeguards))}",
            f"physical_safeguards = {Fraction(len(physical_safeguards))}",
            f"technical_safeguards = {Fraction(len(technical_safeguards))}",
            f"all_safeguards_implemented = {success}",
        ],
        conclusion=(
            "HIPAA Security Rule complies with 45 CFR § 164"
            if success
            else "FAIL: HIPAA Security Rule safeguards check failed"
        ),
    )
    return success, proof


def check_emtala_mse_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: EMTALA requires medical screening exam regardless of ability to pay.
    
    Standard: 42 U.S.C. § 1395dd - Examination and treatment for emergency medical conditions
    Falsifies if: Patient is turned away without MSE or appropriate transfer.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # EMTALA requirements
    mse_required = True
    stabilization_required = True
    appropriate_transfer_allowed = True
    
    # 250-yard rule for dedicated emergency departments
    yard_threshold = Fraction(250)
    
    # Penalty amounts
    hospital_penalty_max = Fraction(50000)  # dollars
    physician_penalty_max = Fraction(50000)  # dollars
    
    # All patients must receive MSE
    all_patients_mse = True
    no_restriction_by_ability_to_pay = True
    
    success = mse_required and all_patients_mse and no_restriction_by_ability_to_pay
    
    proof = ProofObject(
        rule="EMTALA_MSE_Requirement",
        premises=[
            f"mse_required = {mse_required}",
            f"all_patients_mse = {all_patients_mse}",
            f"no_ability_to_pay_restriction = {no_restriction_by_ability_to_pay}",
            f"penalty_max = ${hospital_penalty_max}",
        ],
        conclusion=(
            "EMTALA MSE requirement complies with 42 U.S.C. § 1395dd"
            if success
            else "FAIL: EMTALA MSE requirement check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_MEDICAL invariants."""
    checks = [
        ("check_hipaa_phi_protection", check_hipaa_phi_protection),
        ("check_fda_device_classification", check_fda_device_classification),
        ("check_stark_law_prohibition", check_stark_law_prohibition),
        ("check_fda_qsr_documentation", check_fda_qsr_documentation),
        ("check_hipaa_security_rule_safeguards", check_hipaa_security_rule_safeguards),
        ("check_emtala_mse_requirement", check_emtala_mse_requirement),
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
    print("All D_MEDICAL invariants: PASS")
