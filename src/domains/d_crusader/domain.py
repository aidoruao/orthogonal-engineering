"""D_CRUSADER domain definition — Crusader Fly-Control

Layer: 4
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CRUSADER"
DOMAIN_NAME = "Crusader Fly-Control"
LAYER = 4  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['UV-safety', 'spore-containment', 'detection-accuracy', 'witness']
INVARIANTS = ['UV off when door open.', 'No spores outside unit.', 'Detection accuracy >= 95%.', 'All actions logged in hash chain.']
FALSIFICATION_TESTS = ["F_CRUSADER_001"]
ONTOLOGICAL_ISSUES = ["OI_CRUSADER_001"]
