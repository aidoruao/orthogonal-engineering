"""D_DISABILITYRIGHTS domain definition — Disability Rights

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_DISABILITYRIGHTS"
DOMAIN_NAME = "Disability Rights"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['ada-title-ii', 'ada-title-iii', 'reasonable-accommodation']
INVARIANTS = ['ADA Title II compliance for government services.', 'ADA Title III compliance for public accommodations.', 'Reasonable accommodation process documented.']
FALSIFICATION_TESTS = ["F_DISABILITYRIGHTS_001"]
ONTOLOGICAL_ISSUES = ["OI_DISABILITYRIGHTS_001"]
