"""D_FOOD_SAFETY invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: FSMA (21 U.S.C. §350g), 21 CFR 117, HACCP
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_food_safety.implementation import (
    HACCPSystem,
    FSMAComplianceChecker,
    RecallManagementSystem,
    FoodSafetyAuditor,
    FoodProduct,
    FoodFacility,
    FoodRecall,
    CriticalControlPoint,
    CCPMonitoringRecord,
    HazardType,
    RecallClass,
    FacilityType,
)


def check_critical_limits_not_exceeded() -> bool:
    """
    Invariant: Critical limits must not be exceeded without corrective action.
    Falsification: If CCP deviation doesn't trigger corrective action.
    """
    haccp = HACCPSystem()
    
    # CCP for cooking temperature (min 74°C for poultry)
    cooking_ccp = CriticalControlPoint(
        ccp_id="CCP001",
        hazard=HazardType.BIOLOGICAL,
        description="Cooking temperature",
        critical_limit_min=Fraction(74),  # 74°C minimum
        unit="celsius",
        corrective_action="Continue cooking until temperature reached",
    )
    
    # Temperature within limit
    result = haccp.check_critical_limit(cooking_ccp, Fraction(75))
    assert result["within_limit"] is True, (
        "75°C should be within limit"
    )
    assert result["requires_corrective_action"] is False, (
        "Within limit shouldn't require corrective action"
    )
    
    # Temperature below limit - requires corrective action
    result2 = haccp.check_critical_limit(cooking_ccp, Fraction(65))
    assert result2["within_limit"] is False, (
        "65°C should be below critical limit"
    )
    assert result2["requires_corrective_action"] is True, (
        "Below limit should require corrective action"
    )
    
    return True


def check_facility_registration_required() -> bool:
    """
    Invariant: Manufacturing/processing facilities must register with FDA.
    Falsification: If unregistered manufacturing facility passes compliance.
    """
    checker = FSMAComplianceChecker()
    
    # Unregistered manufacturing facility
    unregistered_facility = FoodFacility(
        facility_id="F001",
        name="Unregistered Plant",
        address="123 Industrial Way",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=False,
    )
    
    result = checker.check_facility_registration(unregistered_facility)
    assert result["compliant"] is False, (
        "Unregistered manufacturing facility should fail"
    )
    
    # Registered facility
    registered_facility = FoodFacility(
        facility_id="F002",
        name="Registered Plant",
        address="456 Factory Blvd",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=True,
        registration_number="FDA123456",
    )
    
    result2 = checker.check_facility_registration(registered_facility)
    assert result2["compliant"] is True, (
        "Registered facility should pass"
    )
    
    # Retail facilities don't need registration
    retail_facility = FoodFacility(
        facility_id="F003",
        name="Grocery Store",
        address="789 Main St",
        facility_type=FacilityType.RETAIL,
        fda_registered=False,
    )
    
    result3 = checker.check_facility_registration(retail_facility)
    assert result3["compliant"] is True, (
        "Retail facility doesn't need FDA registration"
    )
    
    return True


def check_food_safety_plan_required() -> bool:
    """
    Invariant: Manufacturing facilities must have food safety plan with PCQI.
    Falsification: If facility without PCQI or safety plan passes compliance.
    """
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
    
    result = checker.check_food_safety_plan(no_plan_facility)
    assert result["compliant"] is False, (
        "Facility without food safety plan should fail"
    )
    
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
    
    result2 = checker.check_food_safety_plan(no_pcqi_facility)
    assert result2["compliant"] is False, (
        "Facility without PCQI should fail"
    )
    
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
    
    result3 = checker.check_food_safety_plan(compliant_facility)
    assert result3["compliant"] is True, (
        "Facility with safety plan and PCQI should pass"
    )
    
    return True


def check_class_i_recall_immediate() -> bool:
    """
    Invariant: Class I recall requires immediate action.
    Falsification: If Class I recall classified as routine priority.
    """
    system = RecallManagementSystem()
    
    # Class I recall (life-threatening)
    class_i = system.classify_recall("life_threatening", 10000)
    assert class_i["classification"] == RecallClass.CLASS_I, (
        "Life-threatening risk should be Class I"
    )
    assert class_i["urgency"] == "immediate", (
        "Class I should require immediate action"
    )
    assert class_i["press_release_required"] is True, (
        "Class I should require press release"
    )
    
    # Class II recall (temporary/reversible)
    class_ii = system.classify_recall("temporary_reversible", 5000)
    assert class_ii["classification"] == RecallClass.CLASS_II, (
        "Temporary reversible risk should be Class II"
    )
    assert class_ii["urgency"] == "prompt", (
        "Class II should require prompt action"
    )
    
    # Class III recall (unlikely harm)
    class_iii = system.classify_recall("minor_quality_issue", 1000)
    assert class_iii["classification"] == RecallClass.CLASS_III, (
        "Minor issue should be Class III"
    )
    
    return True


def check_recall_recovery_targets() -> bool:
    """
    Invariant: Class I recalls have higher recovery targets than Class III.
    Falsification: If Class III has higher target than Class I.
    """
    system = RecallManagementSystem()
    
    # Class I recall
    class_i_recall = FoodRecall(
        recall_id="R001",
        product_id="P001",
        recall_class=RecallClass.CLASS_I,
        initiation_date=datetime.now(),
        recovered_units=950,
        total_distributed=1000,
    )
    
    class_i_effectiveness = system.check_recall_effectiveness(class_i_recall)
    assert class_i_effectiveness["target_rate"] == 0.95, (
        "Class I should target 95% recovery"
    )
    
    # Class III recall
    class_iii_recall = FoodRecall(
        recall_id="R002",
        product_id="P002",
        recall_class=RecallClass.CLASS_III,
        initiation_date=datetime.now(),
        recovered_units=750,
        total_distributed=1000,
    )
    
    class_iii_effectiveness = system.check_recall_effectiveness(class_iii_recall)
    assert class_iii_effectiveness["target_rate"] == 0.80, (
        "Class III should target 80% recovery"
    )
    
    # Class I target should be higher than Class III
    assert class_i_effectiveness["target_rate"] > class_iii_effectiveness["target_rate"], (
        "Class I target should exceed Class III target"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("critical_limits", check_critical_limits_not_exceeded),
        ("facility_registration", check_facility_registration_required),
        ("food_safety_plan", check_food_safety_plan_required),
        ("class_i_recall", check_class_i_recall_immediate),
        ("recall_recovery", check_recall_recovery_targets),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results
