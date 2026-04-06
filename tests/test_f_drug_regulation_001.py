"""Tests for d_drug_regulation domain."""

from datetime import datetime, timedelta
from fractions import Fraction

from src.domains.d_drug_regulation.implementation import (
    FDADrugApprovalSystem,
    ControlledSubstanceTracker,
    REMSComplianceChecker,
    OffLabelUseEvaluator,
    DrugRegulationEnforcer,
    DrugProduct,
    ClinicalTrial,
    Prescription,
    Pharmacy,
    DrugSchedule,
    ClinicalPhase,
    ApprovalStatus,
    DrugCategory,
    check_schedule_i_status,
    check_prescription_requirement,
    check_renewal_limits,
)


def test_schedule_i_no_medical_use():
    """Test that Schedule I substances have no accepted medical use."""
    drug = DrugProduct(
        product_id="D001",
        brand_name="Illegal",
        generic_name="Prohibited",
        manufacturer="None",
        schedule=DrugSchedule.SCHEDULE_I,
        approved_indications=[],
    )
    
    assert drug.schedule == DrugSchedule.SCHEDULE_I
    assert len(drug.approved_indications) == 0


def test_schedule_ii_with_medical_use():
    """Test that Schedule II substances have accepted medical use."""
    drug = DrugProduct(
        product_id="D002",
        brand_name="Morphine",
        generic_name="Morphine Sulfate",
        manufacturer="PharmaCo",
        schedule=DrugSchedule.SCHEDULE_II,
        approved_indications=["Severe pain"],
    )
    
    assert drug.schedule == DrugSchedule.SCHEDULE_II
    assert len(drug.approved_indications) > 0


def test_drug_requires_nda():
    """Test that approved drugs require NDA."""
    approved = DrugProduct(
        product_id="D003",
        brand_name="Approved",
        generic_name="SafeDrug",
        manufacturer="BigPharma",
        approval_status=ApprovalStatus.APPROVED,
        nda_number="NDA123456",
    )
    
    assert approved.nda_number is not None


def test_rems_requirements():
    """Test REMS requirements for high-risk drugs."""
    checker = REMSComplianceChecker()
    
    rems_drug = DrugProduct(
        product_id="D004",
        brand_name="RiskyMed",
        generic_name="Dangerous",
        manufacturer="CautionPharma",
        has_rems=True,
        rems_elements=["ETASU"],
    )
    
    result = checker.check_rems_requirements(rems_drug)
    assert result["rems_required"] is True


def test_prescription_validity():
    """Test prescription validity checking."""
    tracker = ControlledSubstanceTracker()
    
    rx = Prescription(
        prescription_id="RX001",
        drug_id="D005",
        patient_id="P001",
        prescriber_id="MD001",
        prescriber_dea="DEA123",
        quantity=30,
        dosage="10mg",
        refills_authorized=0,
        written_date=datetime.now(),
        expiration_date=datetime.now() + timedelta(days=30),
    )
    
    result = tracker.check_prescription_validity(rx)
    assert "valid" in result


def test_pharmacy_audit():
    """Test pharmacy compliance audit."""
    enforcer = DrugRegulationEnforcer()
    
    pharmacy = Pharmacy(
        pharmacy_id="PH001",
        name="Test Pharmacy",
        license_number="PHL123",
        dea_registration="DEA123456",
        can_dispense_schedule_ii=True,
    )
    
    result = enforcer.conduct_pharmacy_audit(pharmacy)
    assert result["can_dispense_controlled"] is True


def test_off_label_evaluation():
    """Test off-label use evaluation."""
    evaluator = OffLabelUseEvaluator()
    
    drug = DrugProduct(
        product_id="D006",
        brand_name="Med",
        generic_name="Compound",
        manufacturer="Pharma",
        approved_indications=["Headache"],
    )
    
    result = evaluator.evaluate_off_label_use(drug, "Migraine")
    assert result["off_label"] is True
    assert result["prescription_permitted"] is True


def test_clinical_trial_completion():
    """Test clinical trial completion check."""
    trial = ClinicalTrial(
        trial_id="T001",
        drug_id="D007",
        phase=ClinicalPhase.PHASE_III,
        start_date=datetime.now() - timedelta(days=365),
        target_enrollment=1000,
        actual_enrollment=1000,
        completion_date=datetime.now() - timedelta(days=30),
        primary_endpoint_met=True,
    )
    
    assert trial.is_complete is True
    assert trial.primary_endpoint_met is True


def test_convenience_function_schedule_i():
    """Test convenience function for Schedule I status."""
    result = check_schedule_i_status("Drug", False)
    assert result["schedule_i_eligible"] is True
    
    result2 = check_schedule_i_status("Drug", True)
    assert result2["schedule_i_eligible"] is False


def test_convenience_function_prescription():
    """Test convenience function for prescription requirement."""
    result = check_prescription_requirement(DrugSchedule.SCHEDULE_II)
    assert result["controlled_substance"] is True
    
    result2 = check_prescription_requirement(DrugSchedule.UNCONTROLLED)
    assert result2["controlled_substance"] is False


def test_convenience_function_renewal():
    """Test convenience function for renewal limits."""
    result = check_renewal_limits(DrugSchedule.SCHEDULE_II, 0)
    assert result["renewal_allowed"] is False
    
    result2 = check_renewal_limits(DrugSchedule.SCHEDULE_III, 3)
    assert result2["renewal_allowed"] is True
    assert result2["remaining"] == 2
