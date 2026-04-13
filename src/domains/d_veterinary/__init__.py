"""D_VETERINARY domain — Veterinary Medicine & Animal Welfare — AWA/USDA Compliance.

Layer: 4 (Application)
CardinalStrength: PREDICATIVE
"""

from .domain import DOMAIN_ID, DOMAIN_NAME, LAYER, CARDINAL_STRENGTH
from .implementation import (
    AnimalFacility,
    VeterinaryLicense,
    AnimalTreatment,
    ZoonoticReport,
    EuthanasiaRecord,
)
from .invariants import (
    check_facility_space_compliance,
    check_veterinary_license_valid,
    check_drug_withdrawal_period,
    check_zoonotic_disease_reporting,
    check_euthanasia_compliance,
    check_inspection_currency,
    run_all_invariants,
)

__all__ = [
    "DOMAIN_ID",
    "DOMAIN_NAME",
    "LAYER",
    "CARDINAL_STRENGTH",
    "AnimalFacility",
    "VeterinaryLicense",
    "AnimalTreatment",
    "ZoonoticReport",
    "EuthanasiaRecord",
    "check_facility_space_compliance",
    "check_veterinary_license_valid",
    "check_drug_withdrawal_period",
    "check_zoonotic_disease_reporting",
    "check_euthanasia_compliance",
    "check_inspection_currency",
    "run_all_invariants",
]
