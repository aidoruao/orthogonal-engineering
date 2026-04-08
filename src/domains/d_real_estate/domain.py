"""D_REAL_ESTATE domain definition — Real Estate

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State property codes, Fair Housing Act (lending), disclosure laws
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_REAL_ESTATE"
DOMAIN_NAME = "Real Estate"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "assessment",
    "redlining",
    "disclosure"
]

INVARIANTS = [
    "Property assessment is reproducible.",
    "No race-based lending discrimination (anti-redlining).",
    "Disclosure requirements are enumerated and complete."
]

FALSIFICATION_TESTS = ["F_REAL_ESTATE_001"]
ONTOLOGICAL_ISSUES = ["OI_REAL_ESTATE_001"]
