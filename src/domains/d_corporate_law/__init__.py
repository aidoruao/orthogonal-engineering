"""D_CORPORATE_LAW: Corporate Law (fiduciary duty, self-dealing, corporate veil)

Layer 2 (Statutory) domain implementing corporate governance principles
including fiduciary duties and corporate veil analysis.

Biblical: Luke 16:10 — "Whoever can be trusted with very little
can also be trusted with much, and whoever is dishonest with very
little will also be dishonest with much."
"""

from src.domains.d_corporate_law.implementation import (
    FiduciaryDutyAnalyzer,
    CorporateVeilAnalyzer,
    CorporateComplianceChecker,
    Director,
    CorporateTransaction,
    Shareholder,
    FiduciaryDutyType,
    SelfDealingType,
    check_self_dealing,
)
from src.domains.d_corporate_law.invariants import (
    check_self_dealing_requires_disclosure,
    check_duty_of_loyalty_prevents_self_dealing,
    check_corporate_veil_piercing_factors_cumulative,
)

__all__ = [
    "FiduciaryDutyAnalyzer",
    "CorporateVeilAnalyzer",
    "CorporateComplianceChecker",
    "Director",
    "CorporateTransaction",
    "Shareholder",
    "FiduciaryDutyType",
    "SelfDealingType",
    "check_self_dealing",
    "check_self_dealing_requires_disclosure",
    "check_duty_of_loyalty_prevents_self_dealing",
    "check_corporate_veil_piercing_factors_cumulative",
]
