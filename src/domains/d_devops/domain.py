"""D_DEVOPS domain definition — Devops

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_DEVOPS"
DOMAIN_NAME = "Devops"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_DEVOPS_001"]
ONTOLOGICAL_ISSUES = ["OI_D_DEVOPS_001"]
