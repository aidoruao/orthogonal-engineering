"""D_DISTRIBUTED_SYSTEMS domain definition — Distributed Systems

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_DISTRIBUTED_SYSTEMS"
DOMAIN_NAME = "Distributed Systems"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_DISTRIBUTED_SYSTEMS_001"]
ONTOLOGICAL_ISSUES = ["OI_D_DISTRIBUTED_SYSTEMS_001"]
