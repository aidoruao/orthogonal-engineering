"""D_SEPARATION_OF_POWERS domain definition — Separation of Powers

Layer: 1
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SEPARATION_OF_POWERS"
DOMAIN_NAME = "Separation of Powers"
LAYER = 1
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['executive', 'legislative', 'judicial', 'non-delegation']
INVARIANTS = ['Executive cannot legislate; legislature cannot adjudicate; judiciary cannot enforce.', 'No branch may self-authorize expansion of its own power.']
FALSIFICATION_TESTS = ["F_SEPARATION_OF_POWERS_001"]
ONTOLOGICAL_ISSUES = ["OI_SEPARATION_OF_POWERS_001"]
