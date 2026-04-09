"""D_SUPPLY_CHAIN_SECURITY domain definition — Supply Chain Security

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SUPPLY_CHAIN_SECURITY"
DOMAIN_NAME = "Supply Chain Security"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_SUPPLY_CHAIN_SECURITY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_SUPPLY_CHAIN_SECURITY_001"]
