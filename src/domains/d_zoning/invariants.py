"""D_ZONING invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Fair Housing Act (42 U.S.C. §3601), local zoning ordinances
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_zoning.implementation import (
    ZoneClassifier,
    VarianceEvaluator,
    FairHousingComplianceChecker,
    ZoningComplianceAuditor,
    Parcel,
    ZoningMap,
    VarianceApplication,
    HousingDiscriminationComplaint,
    ZoneType,
    VarianceType,
    HardshipType,
    HousingProtectedClass,
)


def check_zone_classification_deterministic() -> bool:
    """
    Invariant: Zone classification is deterministic given parcel and zoning map.
    Falsification: If same parcel + map produces different classifications.
    """
    classifier = ZoneClassifier()
    
    # Create a parcel
    parcel = Parcel(
        parcel_id="P001",
        address="123 Main St",
        area_sqft=Fraction(10000),
        coordinates=(Fraction(40, 1), Fraction(-74, 1)),
    )
    
    # Create zoning map with explicit parcel assignment
    zoning_map = ZoningMap(
        map_id="ZM001",
        jurisdiction="Test City",
        effective_date=datetime.now(),
        zone_regulations={
            "R1": {"zone_type": ZoneType.RESIDENTIAL, "minimum_lot_size_sqft": 5000},
            "C1": {"zone_type": ZoneType.COMMERCIAL, "minimum_lot_size_sqft": 10000},
        },
        parcel_zoning={
            "P001": "R1",
            "P002": "C1",
        },
    )
    
    # Classify multiple times
    result1 = classifier.classify_parcel(parcel, zoning_map)
    result2 = classifier.classify_parcel(parcel, zoning_map)
    result3 = classifier.classify_parcel(parcel, zoning_map)
    
    # All results should be identical (deterministic)
    assert result1 == result2 == result3, (
        "Zone classification must be deterministic"
    )
    
    # Verify classification succeeded
    assert result1["classified"] is True, (
        "Parcel should be classified"
    )
    assert result1["zone_district"] == "R1", (
        "Parcel should be in R1 zone"
    )
    assert result1["deterministic"] is True, (
        "Classification should be marked deterministic"
    )
    
    return True


def check_variance_requires_documented_hardship() -> bool:
    """
    Invariant: Variance requires documented hardship.
    Falsification: If variance approved without hardship documentation.
    """
    evaluator = VarianceEvaluator()
    
    # Variance without hardship documentation
    variance_no_docs = VarianceApplication(
        application_id="V001",
        parcel_id="P001",
        variance_type=VarianceType.AREA_VARIANCE,
        applicant="John Doe",
        application_date=datetime.now(),
        hardship_claimed=HardshipType.UNNECESSARY_HARDSHIP,
        hardship_documentation=[],  # No documentation!
        unique_conditions_documented=True,
        hardship_not_self_created=True,
        variance_minimum_necessary=True,
        no_detriment_to_public_welfare=True,
        approved=True,  # Approved without docs
    )
    
    result = evaluator.check_variance_decision(variance_no_docs)
    assert result["compliant"] is False, (
        "Variance approved without documentation should be non-compliant"
    )
    
    # Variance with proper documentation
    variance_with_docs = VarianceApplication(
        application_id="V002",
        parcel_id="P002",
        variance_type=VarianceType.USE_VARIANCE,
        applicant="Jane Smith",
        application_date=datetime.now(),
        hardship_claimed=HardshipType.UNIQUE_PROPERTY_CONDITION,
        hardship_documentation=["irregular_lot_survey.pdf", "topography_report.pdf"],
        unique_conditions_documented=True,
        hardship_not_self_created=True,
        variance_minimum_necessary=True,
        no_detriment_to_public_welfare=True,
        approved=True,
    )
    
    result2 = evaluator.evaluate_variance(variance_with_docs)
    assert result2["hardship_documented"] is True, (
        "Variance with documentation should have hardship_documented=True"
    )
    assert result2["eligible_for_approval"] is True, (
        "Properly documented variance should be eligible for approval"
    )
    
    # Denied variance without hardship is compliant
    variance_denied = VarianceApplication(
        application_id="V003",
        parcel_id="P003",
        variance_type=VarianceType.AREA_VARIANCE,
        applicant="Bob Wilson",
        application_date=datetime.now(),
        hardship_claimed=None,
        hardship_documentation=[],
        approved=False,  # Denied
    )
    
    result3 = evaluator.check_variance_decision(variance_denied)
    assert result3["compliant"] is True, (
        "Denied variance is compliant (hardship not required for denial)"
    )
    
    return True


def check_no_exclusionary_zoning() -> bool:
    """
    Invariant: No exclusionary zoning that violates Fair Housing Act.
    Falsification: If zoning with discriminatory impact passes compliance check.
    """
    checker = FairHousingComplianceChecker()
    
    # Zoning with potentially exclusionary large lot requirements
    exclusionary_zoning = ZoningMap(
        map_id="ZM002",
        jurisdiction="Exclusive Town",
        effective_date=datetime.now(),
        zone_regulations={
            "R1": {"zone_type": ZoneType.RESIDENTIAL, "minimum_lot_size_sqft": 87120},  # 2 acres
            "R2": {"zone_type": ZoneType.RESIDENTIAL, "minimum_lot_size_sqft": 43560},  # 1 acre
        },
        parcel_zoning={},
    )
    
    result = checker.check_exclusionary_zoning(exclusionary_zoning, {})
    # Should detect potential violations
    assert len(result["potential_violations"]) > 0, (
        "Large minimum lots should be flagged as potentially exclusionary"
    )
    assert result["compliant"] is False, (
        "Zoning with large minimum lots should not be fully compliant"
    )
    
    # Zoning without exclusionary practices
    inclusive_zoning = ZoningMap(
        map_id="ZM003",
        jurisdiction="Inclusive City",
        effective_date=datetime.now(),
        zone_regulations={
            "R1": {"zone_type": ZoneType.RESIDENTIAL, "minimum_lot_size_sqft": 5000},
            "R2": {"zone_type": ZoneType.RESIDENTIAL, "minimum_lot_size_sqft": 3000},
            "MF": {"zone_type": ZoneType.RESIDENTIAL, "minimum_lot_size_sqft": 10000},
        },
        parcel_zoning={},
    )
    
    result2 = checker.check_exclusionary_zoning(inclusive_zoning, {})
    assert result2["compliant"] is True, (
        "Reasonable lot sizes should be compliant"
    )
    
    return True


def check_variance_all_findings_required() -> bool:
    """
    Invariant: All required findings must be documented for variance approval.
    Falsification: If variance approved with missing findings.
    """
    evaluator = VarianceEvaluator()
    
    # Variance missing required findings
    incomplete_variance = VarianceApplication(
        application_id="V004",
        parcel_id="P004",
        variance_type=VarianceType.AREA_VARIANCE,
        applicant="Incomplete Applicant",
        application_date=datetime.now(),
        hardship_claimed=HardshipType.UNNECESSARY_HARDSHIP,
        hardship_documentation=["docs.pdf"],
        unique_conditions_documented=True,
        hardship_not_self_created=False,  # Missing
        variance_minimum_necessary=False,  # Missing
        no_detriment_to_public_welfare=True,
        approved=True,  # Should not be approved
    )
    
    result = evaluator.evaluate_variance(incomplete_variance)
    assert result["all_findings_met"] is False, (
        "Variance with missing findings should have all_findings_met=False"
    )
    assert result["eligible_for_approval"] is False, (
        "Variance with missing findings should not be eligible for approval"
    )
    
    result2 = evaluator.check_variance_decision(incomplete_variance)
    assert result2["compliant"] is False, (
        "Approved variance without all findings should be non-compliant"
    )
    
    return True


def check_fair_housing_protected_classes() -> bool:
    """
    Invariant: Fair Housing Act protects specific classes.
    Falsification: If protected class is not recognized.
    """
    # Verify all FHA protected classes are defined
    expected_classes = {
        HousingProtectedClass.RACE,
        HousingProtectedClass.COLOR,
        HousingProtectedClass.NATIONAL_ORIGIN,
        HousingProtectedClass.RELIGION,
        HousingProtectedClass.SEX,
        HousingProtectedClass.FAMILIAL_STATUS,
        HousingProtectedClass.DISABILITY,
    }
    
    all_classes = set(HousingProtectedClass)
    
    assert expected_classes.issubset(all_classes), (
        "All FHA protected classes must be defined"
    )
    
    # Create a discrimination complaint
    complaint = HousingDiscriminationComplaint(
        complaint_id="C001",
        parcel_id="P001",
        complainant="Protected Person",
        complaint_date=datetime.now(),
        protected_class=HousingProtectedClass.FAMILIAL_STATUS,
        discrimination_type="zoning",
        description="Zoning ordinance discriminates against families with children",
    )
    
    assert complaint.protected_class == HousingProtectedClass.FAMILIAL_STATUS, (
        "Complaint should record protected class"
    )
    assert complaint.discrimination_type == "zoning", (
        "Complaint should record discrimination type"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("zone_deterministic", check_zone_classification_deterministic),
        ("variance_hardship", check_variance_requires_documented_hardship),
        ("no_exclusionary_zoning", check_no_exclusionary_zoning),
        ("variance_findings", check_variance_all_findings_required),
        ("fair_housing_classes", check_fair_housing_protected_classes),
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
