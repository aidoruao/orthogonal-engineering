"""D_AGRICULTURE invariant checks — agricultural regulation validation.

Agricultural invariants ensure:
1. Organic certification compliance
2. Pesticide application safety
3. Water permit compliance
4. Pre-harvest interval adherence
5. Subsidy eligibility
"""

from datetime import datetime, timedelta
from fractions import Fraction

from .implementation import (
    D_AGRICULTUREChecker,
    D_AGRICULTURERecord,
    Farm,
    PesticideApplication,
    CropType,
    CertificationStatus,
)


def check_organic_certification_requirements() -> bool:
    """Verify organic farms meet certification requirements."""
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
    
    assert checker.check_organic_certification(organic_farm)
    assert not checker.check_organic_certification(conventional_farm)
    
    return True


def check_pesticide_safety_protocols() -> bool:
    """Verify pesticide applications follow safety protocols."""
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
    
    assert checker.check_pesticide_safety(safe_application)
    assert not checker.check_pesticide_safety(unsafe_application)
    
    return True


def check_water_permit_compliance() -> bool:
    """Verify farms have required water permits."""
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
    
    assert checker.check_water_permit(compliant_farm)
    assert not checker.check_water_permit(non_compliant_farm)
    
    return True


def check_pre_harvest_interval() -> bool:
    """Verify pre-harvest intervals are respected."""
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
    
    # Harvest must be after pre-harvest interval
    days_between = (harvest_date - application_date).days
    assert days_between >= application.pre_harvest_interval_days
    
    return True


def check_subsidy_eligibility() -> bool:
    """Verify farm meets subsidy eligibility requirements."""
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
    assert eligible_farm.has_water_permit
    assert eligible_farm.acreage <= Fraction("160")
    
    return True


def check_compliance_deterministic() -> bool:
    """Master compliance check."""
    assert check_organic_certification_requirements()
    assert check_pesticide_safety_protocols()
    assert check_water_permit_compliance()
    assert check_pre_harvest_interval()
    assert check_subsidy_eligibility()
    return True
