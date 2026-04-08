"""D_PARACONSISTENT_LOGIC domain definition — Paraconsistent Logic & Dialetheism

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PARACONSISTENT_LOGIC"
DOMAIN_NAME = "Paraconsistent Logic & Dialetheism"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['paraconsistent', 'dialetheism', 'inconsistency-tolerance', 'four-valued-logic']
INVARIANTS = ['BOTH does not trigger explosion.', 'NEITHER is distinguishable from FALSE.', 'Adding evidence does not demote TRUE to NEITHER.']
FALSIFICATION_TESTS = ["F_PARACONSISTENT_LOGIC_001"]
ONTOLOGICAL_ISSUES = ["OI_PARACONSISTENT_LOGIC_001"]
