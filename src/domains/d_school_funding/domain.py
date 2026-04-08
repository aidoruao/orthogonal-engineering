"""D_SCHOOL_FUNDING domain definition — School Funding

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: Title I (ESEA), state education codes, property tax formulas
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SCHOOL_FUNDING"
DOMAIN_NAME = "School Funding"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "per-pupil",
    "equity",
    "title-i",
    "property-tax"
]

INVARIANTS = [
    "Per-pupil spending variance across districts ≤ equity threshold.",
    "Property tax revenue sharing formula is deterministic.",
    "Title I allocation is formulaic given poverty rate."
]

FALSIFICATION_TESTS = ["F_SCHOOL_FUNDING_001"]
ONTOLOGICAL_ISSUES = ["OI_SCHOOL_FUNDING_001"]
