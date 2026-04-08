"""D_HOUSING_LAW domain definition — Housing & Fair Housing

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_HOUSING_LAW"
DOMAIN_NAME = "Housing & Fair Housing"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['fair-housing-act', 'discrimination', 'reasonable-accommodation']
INVARIANTS = ['No discrimination in sale/rental based on protected class.', 'Reasonable accommodation required for disabilities.', 'Rent control formula (if applicable) is deterministic.']
FALSIFICATION_TESTS = ["F_HOUSING_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_HOUSING_LAW_001"]
