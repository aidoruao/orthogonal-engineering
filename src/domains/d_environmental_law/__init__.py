"""D_ENVIRONMENTAL_LAW: Environmental Law (Clean Air Act, NEPA, permits)

Layer 2 (Statutory) domain implementing environmental law including
Clean Air Act compliance and NEPA review.

Biblical: Genesis 2:15 — "The LORD God took the man and put him in
the Garden of Eden to work it and take care of it."
"""

from src.domains.d_environmental_law.implementation import (
    CleanAirActAnalyzer,
    NEPAAnalyzer,
    PermittingSystem,
    EnvironmentalComplianceChecker,
    EmissionSource,
    AirQualityMonitor,
    FederalAction,
    PollutantType,
    PermitType,
    NEPAClassification,
    AirQualityClass,
    check_emission_permit_requirements,
)
from src.domains.d_environmental_law.invariants import (
    check_naaqs_violation_flagged,
    check_major_source_threshold_100_tpy,
    check_nepa_significant_impact_requires_eis,
)

__all__ = [
    "CleanAirActAnalyzer",
    "NEPAAnalyzer",
    "PermittingSystem",
    "EnvironmentalComplianceChecker",
    "EmissionSource",
    "AirQualityMonitor",
    "FederalAction",
    "PollutantType",
    "PermitType",
    "NEPAClassification",
    "AirQualityClass",
    "check_emission_permit_requirements",
    "check_naaqs_violation_flagged",
    "check_major_source_threshold_100_tpy",
    "check_nepa_significant_impact_requires_eis",
]
