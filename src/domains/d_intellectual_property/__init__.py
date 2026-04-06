"""D_INTELLECTUAL_PROPERTY: Intellectual Property (Patent, Copyright, Trademark)

Layer 2 (Statutory) domain implementing intellectual property law including
patent novelty, copyright fair use, and trademark protection.

Biblical: Exodus 20:15 — "You shall not steal." (includes creative work)
Also: Deuteronomy 24:7 — Protection of person and property rights.
"""

from src.domains.d_intellectual_property.implementation import (
    PatentAnalyzer,
    CopyrightAnalyzer,
    TrademarkAnalyzer,
    Invention,
    CreativeWork,
    Trademark,
    PatentClaim,
    FairUseAnalysis,
    IPType,
    PatentClaimType,
    TrademarkStrength,
    FairUsePurpose,
    check_patent_novelty_required,
    check_copyright_term_limits,
    check_trademark_distinctiveness,
    check_fair_use_factors,
)
from src.domains.d_intellectual_property.invariants import (
    check_patent_novelty_requirement,
    check_copyright_originality_required,
    check_trademark_uniqueness,
    check_fair_use_four_factors,
    check_patent_term_20_years,
)

__all__ = [
    "PatentAnalyzer",
    "CopyrightAnalyzer",
    "TrademarkAnalyzer",
    "Invention",
    "CreativeWork",
    "Trademark",
    "PatentClaim",
    "FairUseAnalysis",
    "IPType",
    "PatentClaimType",
    "TrademarkStrength",
    "FairUsePurpose",
    "check_patent_novelty_required",
    "check_copyright_term_limits",
    "check_trademark_distinctiveness",
    "check_fair_use_factors",
    "check_patent_novelty_requirement",
    "check_copyright_originality_required",
    "check_trademark_uniqueness",
    "check_fair_use_four_factors",
    "check_patent_term_20_years",
]
