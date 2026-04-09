"""D_DATABASE_SYSTEMS domain definition — Database Systems

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_DATABASE_SYSTEMS"
DOMAIN_NAME = "Database Systems"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_DATABASE_SYSTEMS_001"]
ONTOLOGICAL_ISSUES = ["OI_D_DATABASE_SYSTEMS_001"]
