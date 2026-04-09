"""D_SOFTWARE_TESTING domain definition — Software Testing

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SOFTWARE_TESTING"
DOMAIN_NAME = "Software Testing"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_SOFTWARE_TESTING_001"]
ONTOLOGICAL_ISSUES = ["OI_D_SOFTWARE_TESTING_001"]
