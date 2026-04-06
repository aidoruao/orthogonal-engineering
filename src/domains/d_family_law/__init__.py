"""D_FAMILY_LAW: Family Law (custody, child support, best interest)

Layer 2 (Statutory) domain implementing family law principles including
custody determinations and child support calculations.

Biblical: Psalm 127:3 — "Children are a heritage from the LORD,
offspring a reward from him."
"""

from src.domains.d_family_law.implementation import (
    BestInterestAnalyzer,
    ChildSupportCalculator,
    FamilyLawComplianceChecker,
    CustodyEvaluation,
    Parent,
    Child,
    CustodyType,
    CustodyFactor,
    calculate_child_support,
)
from src.domains.d_family_law.invariants import (
    check_best_interest_considers_domestic_violence,
    check_child_support_increases_with_income,
    check_parenting_time_reduces_support,
)

__all__ = [
    "BestInterestAnalyzer",
    "ChildSupportCalculator",
    "FamilyLawComplianceChecker",
    "CustodyEvaluation",
    "Parent",
    "Child",
    "CustodyType",
    "CustodyFactor",
    "calculate_child_support",
    "check_best_interest_considers_domestic_violence",
    "check_child_support_increases_with_income",
    "check_parenting_time_reduces_support",
]
