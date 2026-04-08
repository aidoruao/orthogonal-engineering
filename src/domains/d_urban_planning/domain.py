"""D_URBAN_PLANNING domain definition — Urban Planning

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State planning codes, NEPA, environmental justice policies
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_URBAN_PLANNING"
DOMAIN_NAME = "Urban Planning"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "master-plan",
    "environmental-impact",
    "infrastructure-equity"
]

INVARIANTS = [
    "Master plan is versioned, public, and hash-anchored.",
    "Environmental impact review before development approval.",
    "Infrastructure equity across neighborhoods is measured and reported."
]

FALSIFICATION_TESTS = ["F_URBAN_PLANNING_001"]
ONTOLOGICAL_ISSUES = ["OI_URBAN_PLANNING_001"]
