"""D_MILITARY domain definition — Military and Defense

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MILITARY"
DOMAIN_NAME = "Military and Defense"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['IFF', 'command-control', 'secure-comms']
INVARIANTS = ['IFF does not misclassify friendly as hostile.', 'Autonomous weapon safety interlock cannot be bypassed.']
FALSIFICATION_TESTS = ["F_MILITARY_001"]
ONTOLOGICAL_ISSUES = ["OI_MILITARY_001"]
