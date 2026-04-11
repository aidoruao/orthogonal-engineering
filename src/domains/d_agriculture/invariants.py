"""D_AGRICULTURE invariant checks — agricultural regulation validation.

Agricultural invariants ensure:
1. Organic certification compliance
2. Pesticide application safety
3. Water permit compliance
4. Pre-harvest interval adherence
5. Subsidy eligibility

All functions return Tuple[bool, ProofObject].
falsifies_if: certification requirements violated, safety protocols breached,
             water permits missing, pre-harvest intervals not respected.
"""

from datetime import datetime, timedelta
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    D_AGRICULTUREChecker,
    D_AGRICULTURERecord,
    Farm,
    PesticideApplication,
    CropType,
    CertificationStatus,
)


def check_organic_certification_requirements() -> Tuple[bool, ProofObject]:
    """
    Verify organic farms meet certification requirements.
    
    falsifies_if: organic farm lacks certification OR conventional farm has organic cert
    """
    checker = D_AGRICULTUREChecker()
    
    organic_farm = Farm(
        farm_id="FARM-001",
        name="Green Acres",
        acreage=Fraction("100"),
        crops=[CropType.VEGETABLES, CropType.FRUITS],
        certifications={CertificationStatus.ORGANIC},
        has_water_permit=True,
        has_pesticide_license=False,
    )
    
    conventional_farm = Farm(
        farm_id="FARM-002",
        name="Standard Farm",
        acreage=Fraction("500"),
        crops=[CropType.GRAINS],
        certifications={CertificationStatus.CONVENTIONAL},
        has_water_permit=True,
        has_pesticide_license=True,
    )
    
    organic_result = checker.check_organic_certification(organic_farm)
    conventional_result = checker.check_organic_certification(conventional_farm)
    
    if not organic_result:
        return False, ProofObject(
            rule="organic_certification",
            premises=[f"Farm: {organic_farm.farm_id}", f"Certifications: {organic_farm.certifications}"],
            conclusion="VIOLATION: Organic farm lacks organic certification"
        )
    
    if conventional_result:
        return False, ProofObject(
            rule="organic_certification",
            premises=[f"Farm: {conventional_farm.farm_id}", f"Certifications: {conventional_farm.certifications}"],
            conclusion="VIOLATION: Conventional farm has organic certification"
        )
    
    return True, ProofObject(
        rule="organic_certification",
        premises=["Organic farm certified", "Conventional farm not certified"],
        conclusion="Organic certification requirements satisfied"
    )


def check_pesticide_safety_protocols() -> Tuple[bool, ProofObject]:
    """
    Verify pesticide applications follow safety protocols.
    
    falsifies_if: excessive pesticide application OR missing safety equipment
    """
    checker = D_AGRICULTUREChecker()
    
    safe_application = PesticideApplication(
        application_id="APP-001",
        farm_id="FARM-002",
        chemical_name="SafePest",
        amount_liters=Fraction("10"),
        application_date=datetime(2026, 4, 1),
        pre_harvest_interval_days=14,
        safety_equipment_used=True,
    )
    
    unsafe_application = PesticideApplication(
        application_id="APP-002",
        farm_id="FARM-002",
        chemical_name="ToxicPest",
        amount_liters=Fraction("1000"),  # Excessive
        application_date=datetime(2026, 4, 8),
        pre_harvest_interval_days=0,
        safety_equipment_used=False,
    )
    
    safe_result = checker.check_pesticide_safety(safe_application)
    unsafe_result = checker.check_pesticide_safety(unsafe_application)
    
    if not safe_result:
        return False, ProofObject(
            rule="pesticide_safety",
            premises=[f"Application: {safe_application.application_id}", f"Amount: {safe_application.amount_liters}L"],
            conclusion="VIOLATION: Safe pesticide application flagged as unsafe"
        )
    
    if unsafe_result:
        return False, ProofObject(
            rule="pesticide_safety",
            premises=[f"Application: {unsafe_application.application_id}", f"Amount: {unsafe_application.amount_liters}L", f"Safety equipment: {unsafe_application.safety_equipment_used}"],
            conclusion="VIOLATION: Unsafe pesticide application passed safety check"
        )
    
    return True, ProofObject(
        rule="pesticide_safety",
        premises=["Safe application approved", "Unsafe application rejected"],
        conclusion="Pesticide safety protocols satisfied"
    )


def check_water_permit_compliance() -> Tuple[bool, ProofObject]:
    """
    Verify farms have required water permits.
    
    falsifies_if: farm lacks required water permit
    """
    checker = D_AGRICULTUREChecker()
    
    compliant_farm = Farm(
        farm_id="FARM-003",
        name="WaterWise Farm",
        acreage=Fraction("200"),
        crops=[CropType.GRAINS],
        certifications={CertificationStatus.CONVENTIONAL},
        has_water_permit=True,
        has_pesticide_license=True,
    )
    
    non_compliant_farm = Farm(
        farm_id="FARM-004",
        name="Dry Farm",
        acreage=Fraction("50"),
        crops=[CropType.VEGETABLES],
        certifications={CertificationStatus.CONVENTIONAL},
        has_water_permit=False,
        has_pesticide_license=False,
    )
    
    compliant_result = checker.check_water_permit(compliant_farm)
    non_compliant_result = checker.check_water_permit(non_compliant_farm)
    
    if not compliant_result:
        return False, ProofObject(
            rule="water_permit",
            premises=[f"Farm: {compliant_farm.farm_id}", f"Has permit: {compliant_farm.has_water_permit}"],
            conclusion="VIOLATION: Compliant farm failed water permit check"
        )
    
    if non_compliant_result:
        return False, ProofObject(
            rule="water_permit",
            premises=[f"Farm: {non_compliant_farm.farm_id}", f"Has permit: {non_compliant_farm.has_water_permit}"],
            conclusion="VIOLATION: Non-compliant farm passed water permit check"
        )
    
    return True, ProofObject(
        rule="water_permit",
        premises=["Compliant farm approved", "Non-compliant farm rejected"],
        conclusion="Water permit compliance satisfied"
    )


def check_pre_harvest_interval() -> Tuple[bool, ProofObject]:
    """
    Verify pre-harvest intervals are respected.
    
    falsifies_if: harvest occurs before pre-harvest interval expires
    """
    application_date = datetime(2026, 4, 1)
    harvest_date = datetime(2026, 4, 20)  # 19 days later
    
    application = PesticideApplication(
        application_id="APP-003",
        farm_id="FARM-002",
        chemical_name="CropSafe",
        amount_liters=Fraction("5"),
        application_date=application_date,
        pre_harvest_interval_days=14,
        safety_equipment_used=True,
    )
    
    days_between = (harvest_date - application_date).days
    
    if days_between < application.pre_harvest_interval_days:
        return False, ProofObject(
            rule="pre_harvest_interval",
            premises=[f"Days between: {days_between}", f"Required: {application.pre_harvest_interval_days}"],
            conclusion="VIOLATION: Harvest occurred before pre-harvest interval"
        )
    
    return True, ProofObject(
        rule="pre_harvest_interval",
        premises=[f"Days between: {days_between}", f"Required: {application.pre_harvest_interval_days}"],
        conclusion="Pre-harvest interval respected"
    )


def check_subsidy_eligibility() -> Tuple[bool, ProofObject]:
    """
    Verify farm meets subsidy eligibility requirements.
    
    falsifies_if: farm exceeds size limit OR lacks water permit
    """
    eligible_farm = Farm(
        farm_id="FARM-005",
        name="Small Farm",
        acreage=Fraction("150"),  # Under 160 acres for small farm subsidy
        crops=[CropType.GRAINS],
        certifications={CertificationStatus.CONVENTIONAL},
        has_water_permit=True,
        has_pesticide_license=True,
    )
    
    # Eligibility: water permit + under size limit
    if not eligible_farm.has_water_permit:
        return False, ProofObject(
            rule="subsidy_eligibility",
            premises=[f"Farm: {eligible_farm.farm_id}", f"Water permit: {eligible_farm.has_water_permit}"],
            conclusion="VIOLATION: Farm lacks water permit for subsidy"
        )
    
    if eligible_farm.acreage > Fraction("160"):
        return False, ProofObject(
            rule="subsidy_eligibility",
            premises=[f"Farm: {eligible_farm.farm_id}", f"Acreage: {eligible_farm.acreage}", "Limit: 160"],
            conclusion="VIOLATION: Farm exceeds size limit for subsidy"
        )
    
    return True, ProofObject(
        rule="subsidy_eligibility",
        premises=[f"Acreage: {eligible_farm.acreage}", "Limit: 160", "Water permit: yes"],
        conclusion="Subsidy eligibility requirements satisfied"
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """
    Master compliance check.
    
    Returns aggregate result of all compliance checks.
    """
    checks = [
        check_organic_certification_requirements(),
        check_pesticide_safety_protocols(),
        check_water_permit_compliance(),
        check_pre_harvest_interval(),
        check_subsidy_eligibility(),
    ]
    
    failed = [(i, proof) for i, (ok, proof) in enumerate(checks) if not ok]
    
    if failed:
        check_names = ["organic", "pesticide", "water", "pre-harvest", "subsidy"]
        failed_names = [check_names[i] for i, _ in failed]
        return False, ProofObject(
            rule="master_compliance",
            premises=[f"Failed checks: {failed_names}"],
            conclusion=f"VIOLATION: {len(failed)} compliance checks failed"
        )
    
    return True, ProofObject(
        rule="master_compliance",
        premises=["All 5 compliance checks passed"],
        conclusion="Master compliance check satisfied"
    )
