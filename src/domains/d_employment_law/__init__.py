"""D_EMPLOYMENT_LAW: Employment Law (Title VII, ADA, ADEA, FMLA)

Layer 2 (Statutory) domain implementing employment law including
anti-discrimination, accommodation requirements, and leave entitlements.

Imports from D_LABOR_RIGHTS where applicable (NLRA intersection).

Biblical: James 5:4 — "Look! The wages you failed to pay the workers
who mowed your fields are crying out against you."
"""

from src.domains.d_employment_law.implementation import (
    TitleVIIAnalyzer,
    ADAAccommodationAnalyzer,
    FMLAEligibilityChecker,
    WageHourCompliance,
    Employee,
    EmploymentAction,
    DiscriminationClaim,
    AccommodationRequest,
    ProtectedClass,
    FMLAQualifyingReason,
    EmploymentActionType,
    check_title_vii_prohibits_discrimination,
    check_ada_accommodation_required,
    check_fmla_eligibility,
)
from src.domains.d_employment_law.invariants import (
    check_title_vii_protected_classes,
    check_ada_interactive_process,
    check_fmla_12_weeks_entitlement,
    check_wage_theft_prohibited,
    check_at_will_exceptions,
)

__all__ = [
    "TitleVIIAnalyzer",
    "ADAAccommodationAnalyzer",
    "FMLAEligibilityChecker",
    "WageHourCompliance",
    "Employee",
    "EmploymentAction",
    "DiscriminationClaim",
    "AccommodationRequest",
    "ProtectedClass",
    "FMLAQualifyingReason",
    "EmploymentActionType",
    "check_title_vii_prohibits_discrimination",
    "check_ada_accommodation_required",
    "check_fmla_eligibility",
    "check_title_vii_protected_classes",
    "check_ada_interactive_process",
    "check_fmla_12_weeks_entitlement",
    "check_wage_theft_prohibited",
    "check_at_will_exceptions",
]
