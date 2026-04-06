"""D_HOUSING_LAW: Housing Law (Fair Housing Act, tenant rights, eviction)

Layer 2 (Statutory) domain implementing housing law including fair housing,
tenant rights, and eviction process protections.

Biblical: Nehemiah 5:1-13 — Oppose housing oppression and unjust debt.
"""

from src.domains.d_housing_law.implementation import (
    FairHousingAnalyzer,
    EvictionProcess,
    TenantRights,
    HousingDiscriminationComplaint,
    LeaseAgreement,
    ProtectedClass,
    EvictionNoticeType,
    HabitabilityRequirement,
)
from src.domains.d_housing_law.invariants import (
    check_protected_classes_enumerated,
    check_eviction_notice_required,
    check_habitability_minimum_standards,
    check_fair_housing_prohibits_discrimination,
    check_retaliation_prohibited,
)

__all__ = [
    "FairHousingAnalyzer",
    "EvictionProcess",
    "TenantRights",
    "HousingDiscriminationComplaint",
    "LeaseAgreement",
    "ProtectedClass",
    "EvictionNoticeType",
    "HabitabilityRequirement",
    "check_protected_classes_enumerated",
    "check_eviction_notice_required",
    "check_habitability_minimum_standards",
    "check_fair_housing_prohibits_discrimination",
    "check_retaliation_prohibited",
]
