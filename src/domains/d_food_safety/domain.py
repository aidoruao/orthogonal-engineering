"""D_FOOD_SAFETY domain definition — Food Safety

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: FSMA (21 U.S.C. §350g), FD&C Act (21 U.S.C. §301), 21 CFR 117, HACCP
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FOOD_SAFETY"
DOMAIN_NAME = "Food Safety"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "haccp",
    "inspection",
    "recall"
]

INVARIANTS = [
    "HACCP plan required and verified for all facilities.",
    "Inspection frequency is deterministic per risk level.",
    "Recall trigger is formulaic given defect reports."
]

FALSIFICATION_TESTS = ["F_FOOD_001"]
ONTOLOGICAL_ISSUES = ["OI_FOOD_001"]
