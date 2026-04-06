"""D_IMMIGRATION: Immigration Law (INA, visa categories, asylum, due process link)

Layer 2 (Statutory) domain implementing immigration law including
visa preferences, asylum analysis, and removal defense.

Links to Layer 1: Due process protections in removal proceedings.

Biblical: Leviticus 19:34 — "The foreigner residing among you must
be treated as your native-born. Love them as yourself, for you were
foreigners in Egypt."
"""

from src.domains.d_immigration.implementation import (
    VisaPreferenceSystem,
    AsylumAnalyzer,
    RemovalDefenseAnalyzer,
    ImmigrationComplianceChecker,
    Alien,
    VisaApplication,
    AsylumClaim,
    VisaCategory,
    AdmissionClass,
    check_visa_category_eligibility,
)
from src.domains.d_immigration.invariants import (
    check_asylum_requires_protected_nexus,
    check_due_process_rights_in_removal,
    check_visa_allocation_family_plus_employment,
)

__all__ = [
    "VisaPreferenceSystem",
    "AsylumAnalyzer",
    "RemovalDefenseAnalyzer",
    "ImmigrationComplianceChecker",
    "Alien",
    "VisaApplication",
    "AsylumClaim",
    "VisaCategory",
    "AdmissionClass",
    "check_visa_category_eligibility",
    "check_asylum_requires_protected_nexus",
    "check_due_process_rights_in_removal",
    "check_visa_allocation_family_plus_employment",
]
