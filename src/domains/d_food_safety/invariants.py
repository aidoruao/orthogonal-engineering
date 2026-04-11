"""D_FOOD_SAFETY invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Federal Food, Drug, and Cosmetic Act (21 U.S.C. §301 et seq.)
- Food Safety Modernization Act (FSMA) (21 U.S.C. §350g)
- HACCP (Hazard Analysis Critical Control Points) principles
- 21 CFR Part 117 (Preventive Controls for Human Food)

Source: ontology/ontology.json#D_FOOD_SAFETY
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple
from datetime import datetime, timedelta

from axioms.logic import ProofObject

from src.domains.d_food_safety.implementation import (
    HACCPSystem,
    FSMAComplianceChecker,
    RecallManagementSystem,
    FoodFacility,
    FoodRecall,
    CriticalControlPoint,
    HazardType,
    RecallClass,
    FacilityType,
)


def check_critical_limits_enforced() -> Tuple[bool, ProofObject]:
    """
    Invariant: Critical limits at CCPs must not be exceeded without corrective action.
    
    Standard: 21 CFR 117.150 (corrective actions); HACCP Principle 5
    Falsifies if: CCP deviation does not trigger corrective action requirement.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    haccp = HACCPSystem()
    
    # CCP for cooking temperature (min 74°C for poultry)
    cooking_ccp = CriticalControlPoint(
        ccp_id="CCP001",
        hazard=HazardType.BIOLOGICAL,
        description="Cooking temperature",
        critical_limit_min=Fraction(74),
        unit="celsius",
        corrective_action="Continue cooking until temperature reached",
    )
    
    # Temperature within limit
    result_safe = haccp.check_critical_limit(cooking_ccp, Fraction(75))
    within_limit = result_safe["within_limit"] is True
    no_action_needed = result_safe["requires_corrective_action"] is False
    
    # Temperature below limit - requires corrective action
    result_violation = haccp.check_critical_limit(cooking_ccp, Fraction(65))
    below_limit = result_violation["within_limit"] is False
    action_required = result_violation["requires_corrective_action"] is True
    
    success = within_limit and no_action_needed and below_limit and action_required
    
    proof = ProofObject(
        rule="CriticalLimitsEnforced",
        premises=[
            f"safe_temp_within_limit = {within_limit}",
            f"safe_no_action_needed = {no_action_needed}",
            f"violation_below_limit = {below_limit}",
            f"violation_action_required = {action_required}",
        ],
        conclusion=(
            "HACCP critical limits enforced with corrective actions"
            if success
            else "FAIL: Critical limits not enforced"
        ),
    )
    return success, proof


def check_facility_registration_required() -> Tuple[bool, ProofObject]:
    """
    Invariant: Manufacturing/processing facilities must register with FDA.
    
    Standard: 21 U.S.C. §350d; FSMA Section 102
    Falsifies if: Unregistered manufacturing facility passes compliance.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    checker = FSMAComplianceChecker()
    
    # Unregistered manufacturing facility
    unregistered_facility = FoodFacility(
        facility_id="F001",
        name="Unregistered Plant",
        address="123 Industrial Way",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=False,
    )
    
    result_unregistered = checker.check_facility_registration(unregistered_facility)
    unregistered_fails = result_unregistered["compliant"] is False
    
    # Registered facility
    registered_facility = FoodFacility(
        facility_id="F002",
        name="Registered Plant",
        address="456 Factory Blvd",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=True,
        registration_number="FDA123456",
    )
    
    result_registered = checker.check_facility_registration(registered_facility)
    registered_passes = result_registered["compliant"] is True
    
    # Retail facilities don't need registration
    retail_facility = FoodFacility(
        facility_id="F003",
        name="Grocery Store",
        address="789 Main St",
        facility_type=FacilityType.RETAIL,
        fda_registered=False,
    )
    
    result_retail = checker.check_facility_registration(retail_facility)
    retail_exempt = result_retail["compliant"] is True
    
    success = unregistered_fails and registered_passes and retail_exempt
    
    proof = ProofObject(
        rule="FacilityRegistrationRequired",
        premises=[
            f"unregistered_manufacturing_fails = {unregistered_fails}",
            f"registered_facility_passes = {registered_passes}",
            f"retail_exemption_applies = {retail_exempt}",
        ],
        conclusion=(
            "21 U.S.C. §350d facility registration requirements enforced"
            if success
            else "FAIL: Facility registration requirements not enforced"
        ),
    )
    return success, proof


def check_food_safety_plan_requirements() -> Tuple[bool, ProofObject]:
    """
    Invariant: Manufacturing facilities must have food safety plan with PCQI.
    
    Standard: 21 CFR 117.126 (food safety plan); 21 CFR 117.180 (PCQI)
    Falsifies if: Facility without safety plan or PCQI passes compliance.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    checker = FSMAComplianceChecker()
    
    # Facility without safety plan
    no_plan_facility = FoodFacility(
        facility_id="F004",
        name="No Plan Plant",
        address="321 Plant Way",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=True,
        has_food_safety_plan=False,
        preventive_controls_qualified_individual=None,
    )
    
    result_no_plan = checker.check_food_safety_plan(no_plan_facility)
    no_plan_fails = result_no_plan["compliant"] is False
    
    # Facility without PCQI
    no_pcqi_facility = FoodFacility(
        facility_id="F005",
        name="No PCQI Plant",
        address="654 Plant St",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=True,
        has_food_safety_plan=True,
        preventive_controls_qualified_individual=None,
    )
    
    result_no_pcqi = checker.check_food_safety_plan(no_pcqi_facility)
    no_pcqi_fails = result_no_pcqi["compliant"] is False
    
    # Compliant facility
    compliant_facility = FoodFacility(
        facility_id="F006",
        name="Compliant Plant",
        address="987 Safe Way",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=True,
        has_food_safety_plan=True,
        preventive_controls_qualified_individual="John Doe, PCQI",
    )
    
    result_compliant = checker.check_food_safety_plan(compliant_facility)
    compliant_passes = result_compliant["compliant"] is True
    
    success = no_plan_fails and no_pcqi_fails and compliant_passes
    
    proof = ProofObject(
        rule="FoodSafetyPlanRequirements",
        premises=[
            f"no_plan_fails = {no_plan_fails}",
            f"no_pcqi_fails = {no_pcqi_fails}",
            f"compliant_passes = {compliant_passes}",
        ],
        conclusion=(
            "21 CFR 117.126 food safety plan requirements enforced"
            if success
            else "FAIL: Food safety plan requirements not enforced"
        ),
    )
    return success, proof


def check_recall_classification_urgency() -> Tuple[bool, ProofObject]:
    """
    Invariant: Class I recalls require immediate action with press release.
    
    Standard: 21 CFR 7.3 (recall definitions); 21 CFR 7.53 (public warning)
    Falsifies if: Class I recall classified as routine or press release not required.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    system = RecallManagementSystem()
    
    # Class I recall (life-threatening)
    class_i = system.classify_recall("life_threatening", 10000)
    class_i_correct = class_i["classification"] == RecallClass.CLASS_I
    class_i_urgent = class_i["urgency"] == "immediate"
    class_i_press = class_i["press_release_required"] is True
    
    # Class II recall (temporary/reversible)
    class_ii = system.classify_recall("temporary_reversible", 5000)
    class_ii_correct = class_ii["classification"] == RecallClass.CLASS_II
    class_ii_prompt = class_ii["urgency"] == "prompt"
    
    # Class III recall (unlikely harm)
    class_iii = system.classify_recall("minor_quality_issue", 1000)
    class_iii_correct = class_iii["classification"] == RecallClass.CLASS_III
    
    success = (
        class_i_correct and class_i_urgent and class_i_press and
        class_ii_correct and class_ii_prompt and
        class_iii_correct
    )
    
    proof = ProofObject(
        rule="RecallClassificationUrgency",
        premises=[
            f"class_i_correct = {class_i_correct}",
            f"class_i_immediate = {class_i_urgent}",
            f"class_i_press_required = {class_i_press}",
            f"class_ii_correct = {class_ii_correct}",
            f"class_iii_correct = {class_iii_correct}",
        ],
        conclusion=(
            "21 CFR 7.3 recall classification requirements enforced"
            if success
            else "FAIL: Recall classification requirements not enforced"
        ),
    )
    return success, proof


def check_recall_effectiveness_targets() -> Tuple[bool, ProofObject]:
    """
    Invariant: Class I recalls have higher recovery targets than Class III.
    
    Standard: 21 CFR 7.53 (recall effectiveness); FDA recall monitoring guidance
    Falsifies if: Class III has higher or equal target than Class I.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    system = RecallManagementSystem()
    
    # Class I recall target
    class_i_recall = FoodRecall(
        recall_id="R001",
        product_id="P001",
        recall_class=RecallClass.CLASS_I,
        initiation_date=datetime.now(),
        recovered_units=950,
        total_distributed=1000,
    )
    
    class_i_effectiveness = system.check_recall_effectiveness(class_i_recall)
    class_i_target = Fraction(95, 100)
    class_i_correct = class_i_effectiveness["target_rate"] == class_i_target
    
    # Class III recall target
    class_iii_recall = FoodRecall(
        recall_id="R002",
        product_id="P002",
        recall_class=RecallClass.CLASS_III,
        initiation_date=datetime.now(),
        recovered_units=750,
        total_distributed=1000,
    )
    
    class_iii_effectiveness = system.check_recall_effectiveness(class_iii_recall)
    class_iii_target = Fraction(80, 100)
    class_iii_correct = class_iii_effectiveness["target_rate"] == class_iii_target
    
    # Class I target higher than Class III
    target_hierarchy = class_i_target > class_iii_target
    
    success = class_i_correct and class_iii_correct and target_hierarchy
    
    proof = ProofObject(
        rule="RecallEffectivenessTargets",
        premises=[
            f"class_i_target_95% = {class_i_correct}",
            f"class_iii_target_80% = {class_iii_correct}",
            f"class_i_higher_than_iii = {target_hierarchy}",
        ],
        conclusion=(
            "Recall effectiveness targets properly tiered by class"
            if success
            else "FAIL: Recall effectiveness targets misconfigured"
        ),
    )
    return success, proof


def check_supply_chain_verification() -> Tuple[bool, ProofObject]:
    """
    Invariant: Supply chain verification required for hazards requiring control.
    
    Standard: 21 CFR 117.405 (supply chain program)
    Falsifies if: Unverified supplier for controlled hazard passes compliance.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    checker = FSMAComplianceChecker()
    
    # Hazard requiring control, unverified supplier
    result_unverified = checker.check_supply_chain_program(
        supplier_verified=False,
        hazard_requiring_control=True,
    )
    unverified_fails = result_unverified["compliant"] is False
    
    # Hazard requiring control, verified supplier
    result_verified = checker.check_supply_chain_program(
        supplier_verified=True,
        hazard_requiring_control=True,
    )
    verified_passes = result_verified["compliant"] is True
    
    # No hazard requiring control, unverified OK
    result_no_hazard = checker.check_supply_chain_program(
        supplier_verified=False,
        hazard_requiring_control=False,
    )
    no_hazard_passes = result_no_hazard["compliant"] is True
    
    success = unverified_fails and verified_passes and no_hazard_passes
    
    proof = ProofObject(
        rule="SupplyChainVerification",
        premises=[
            f"unverified_with_hazard_fails = {unverified_fails}",
            f"verified_with_hazard_passes = {verified_passes}",
            f"no_hazard_exemption = {no_hazard_passes}",
        ],
        conclusion=(
            "21 CFR 117.405 supply chain verification requirements enforced"
            if success
            else "FAIL: Supply chain verification requirements not enforced"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_FOOD_SAFETY invariants."""
    checks = [
        ("check_critical_limits_enforced", check_critical_limits_enforced),
        ("check_facility_registration_required", check_facility_registration_required),
        ("check_food_safety_plan_requirements", check_food_safety_plan_requirements),
        ("check_recall_classification_urgency", check_recall_classification_urgency),
        ("check_recall_effectiveness_targets", check_recall_effectiveness_targets),
        ("check_supply_chain_verification", check_supply_chain_verification),
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
    print("All D_FOOD_SAFETY invariants: PASS")
