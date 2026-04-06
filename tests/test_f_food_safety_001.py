"""Tests for d_food_safety domain."""

from datetime import datetime, timedelta
from fractions import Fraction

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
    check_critical_limit_exceeded,
    check_class_i_recall_requirement,
    check_temperature_danger_zone,
)


def test_critical_limit_check():
    """Test critical limit checking."""
    haccp = HACCPSystem()
    
    ccp = CriticalControlPoint(
        ccp_id="CCP001",
        hazard=HazardType.BIOLOGICAL,
        description="Cooking temp",
        critical_limit_min=Fraction(74),
        unit="celsius",
    )
    
    result = haccp.check_critical_limit(ccp, Fraction(75))
    assert result["within_limit"] is True
    
    result2 = haccp.check_critical_limit(ccp, Fraction(65))
    assert result2["within_limit"] is False
    assert result2["requires_corrective_action"] is True


def test_hazard_risk_analysis():
    """Test hazard risk analysis."""
    haccp = HACCPSystem()
    
    product = FoodProduct(
        product_id="P001",
        product_name="Chicken",
        manufacturer_id="M001",
        is_rte=True,
    )
    
    result = haccp.analyze_hazard_risk(HazardType.BIOLOGICAL, product)
    assert result["hazard"] == "BIOLOGICAL"
    assert result["ccp_required"] is True


def test_facility_registration():
    """Test facility registration check."""
    checker = FSMAComplianceChecker()
    
    unregistered = FoodFacility(
        facility_id="F001",
        name="Unregistered",
        address="123 Plant",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=False,
    )
    
    result = checker.check_facility_registration(unregistered)
    assert result["compliant"] is False


def test_food_safety_plan():
    """Test food safety plan check."""
    checker = FSMAComplianceChecker()
    
    no_plan = FoodFacility(
        facility_id="F002",
        name="No Plan",
        address="456 Plant",
        facility_type=FacilityType.MANUFACTURING,
        has_food_safety_plan=False,
    )
    
    result = checker.check_food_safety_plan(no_plan)
    assert result["compliant"] is False


def test_recall_classification():
    """Test recall classification."""
    system = RecallManagementSystem()
    
    class_i = system.classify_recall("life_threatening", 10000)
    assert class_i["classification"] == RecallClass.CLASS_I
    assert class_i["urgency"] == "immediate"


def test_recall_effectiveness():
    """Test recall effectiveness check."""
    system = RecallManagementSystem()
    
    recall = FoodRecall(
        recall_id="R001",
        product_id="P001",
        recall_class=RecallClass.CLASS_I,
        initiation_date=datetime.now(),
        recovered_units=950,
        total_distributed=1000,
    )
    
    result = system.check_recall_effectiveness(recall)
    assert result["target_rate"] == 0.95
    assert result["meeting_target"] is True


def test_supply_chain_verification():
    """Test supply chain verification."""
    checker = FSMAComplianceChecker()
    
    result = checker.check_supply_chain_program(
        supplier_verified=False,
        hazard_requiring_control=True,
    )
    assert result["compliant"] is False


def test_facility_audit():
    """Test comprehensive facility audit."""
    auditor = FoodSafetyAuditor()
    
    facility = FoodFacility(
        facility_id="F003",
        name="Test Plant",
        address="789 Plant",
        facility_type=FacilityType.MANUFACTURING,
        fda_registered=True,
        has_food_safety_plan=True,
        preventive_controls_qualified_individual="PCQI",
    )
    
    result = auditor.conduct_facility_audit(facility)
    assert result["registration_compliant"] is True
    assert result["safety_plan_compliant"] is True


def test_convenience_function_critical_limit():
    """Test convenience function for critical limit."""
    result = check_critical_limit_exceeded(75.0, 74.0)
    assert result["critical_limit_exceeded"] is True
    
    result2 = check_critical_limit_exceeded(70.0, 74.0)
    assert result2["critical_limit_exceeded"] is False


def test_convenience_function_class_i():
    """Test convenience function for Class I recall."""
    result = check_class_i_recall_requirement("life_threatening")
    assert result["class_i_required"] is True
    assert result["immediate_action_required"] is True
    
    result2 = check_class_i_recall_requirement("minor_issue")
    assert result2["class_i_required"] is False


def test_convenience_function_danger_zone():
    """Test convenience function for temperature danger zone."""
    result = check_temperature_danger_zone(300, 25)  # 5 hours at 25°C
    assert result["in_danger_zone"] is True
    assert result["time_exceeded"] is True
    assert result["discard_required"] is True
