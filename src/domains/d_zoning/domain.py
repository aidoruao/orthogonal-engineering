"""D_ZONING domain definition — Zoning

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: Fair Housing Act (42 U.S.C. §3601), zoning ordinances, variance procedures
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ZONING"
DOMAIN_NAME = "Zoning"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "zone-classification",
    "variance",
    "fair-housing"
]

INVARIANTS = [
    "Zone classification is deterministic given parcel and zoning map.",
    "Variance requires documented hardship.",
    "No exclusionary zoning that violates Fair Housing Act."
]

FALSIFICATION_TESTS = ["F_ZONING_001"]
ONTOLOGICAL_ISSUES = ["OI_ZONING_001"]
