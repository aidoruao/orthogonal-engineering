"""D_TREATIES domain definition — Treaty Obligations

Layer: 0
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_TREATIES"
DOMAIN_NAME = "Treaty Obligations"
LAYER = 0
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['supremacy', 'ratification', 'withdrawal']
INVARIANTS = ['Ratified treaty provisions override conflicting domestic statute.', 'Treaty withdrawal requires documented notice period and cannot be retroactive.']
FALSIFICATION_TESTS = ["F_TREATIES_001"]
ONTOLOGICAL_ISSUES = ["OI_TREATIES_001"]
