"""D_NETWORKING domain definition — Networking

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_NETWORKING"
DOMAIN_NAME = "Networking"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_NETWORKING_001"]
ONTOLOGICAL_ISSUES = ["OI_D_NETWORKING_001"]
