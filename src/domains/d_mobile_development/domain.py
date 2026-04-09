"""D_MOBILE_DEVELOPMENT domain definition — Mobile Development

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MOBILE_DEVELOPMENT"
DOMAIN_NAME = "Mobile Development"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_MOBILE_DEVELOPMENT_001"]
ONTOLOGICAL_ISSUES = ["OI_D_MOBILE_DEVELOPMENT_001"]
