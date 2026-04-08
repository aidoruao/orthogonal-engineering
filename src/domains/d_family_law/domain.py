"""D_FAMILY_LAW domain definition — Family Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FAMILY_LAW"
DOMAIN_NAME = "Family Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['custody', 'child-support', 'best-interest']
INVARIANTS = ['Best interest of child is the paramount standard.', 'Custody determination is documented with all factors considered.', 'Child support calculation follows state formula deterministically.']
FALSIFICATION_TESTS = ["F_FAMILY_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_FAMILY_LAW_001"]
