"""D_BUILDING_CODES domain definition — Building Codes

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: International Building Code (IBC), NFPA, ADA Standards
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BUILDING_CODES"
DOMAIN_NAME = "Building Codes"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "ibc",
    "structural-load",
    "fire-egress",
    "ada"
]

INVARIANTS = [
    "Structural load calculations within IBC tolerance.",
    "Fire egress requirements met for occupancy type.",
    "ADA accessibility enforced for public accommodations."
]

FALSIFICATION_TESTS = ["F_BUILDING_CODES_001"]
ONTOLOGICAL_ISSUES = ["OI_BUILDING_CODES_001"]
