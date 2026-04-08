"""D_INTERNATIONAL_HUMANITARIAN domain definition — International Humanitarian Law

Layer: 0
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_INTERNATIONAL_HUMANITARIAN"
DOMAIN_NAME = "International Humanitarian Law"
LAYER = 0
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['geneva-conventions', 'distinction', 'proportionality']
INVARIANTS = ['Distinction between combatants and civilians is maintained at all times.', 'Use of force must be proportional to military objective.']
FALSIFICATION_TESTS = ["F_INTERNATIONAL_HUMANITARIAN_001"]
ONTOLOGICAL_ISSUES = ["OI_INTERNATIONAL_HUMANITARIAN_001"]
