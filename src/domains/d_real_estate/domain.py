"""D_REALESTATE domain definition — Real Estate Regulation

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_REALESTATE"
DOMAIN_NAME = "Real Estate Regulation"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['assessment', 'redlining', 'disclosure']

INVARIANTS = ['Property assessment is reproducible.', 'No race-based lending discrimination (anti-redlining).', 'Disclosure requirements are enumerated and complete.']

FALSIFICATION_TESTS = ["F_REALESTATE_001"]
ONTOLOGICAL_ISSUES = ["OI_REALESTATE_001"]
