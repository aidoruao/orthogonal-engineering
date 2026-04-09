"""D_CRYPTOGRAPHY domain definition — Cryptography

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CRYPTOGRAPHY"
DOMAIN_NAME = "Cryptography"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_CRYPTOGRAPHY_001"]
ONTOLOGICAL_ISSUES = ["OI_D_CRYPTOGRAPHY_001"]
