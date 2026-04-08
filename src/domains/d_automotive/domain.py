"""D_AUTOMOTIVE domain definition — Automotive

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AUTOMOTIVE"
DOMAIN_NAME = "Automotive"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['AUTOSAR', 'ISO-26262', 'OTA', 'CAN-bus']
INVARIANTS = ['OTA update rejected if signature invalid.', 'CAN bus message timing within spec.']
FALSIFICATION_TESTS = ["F_AUTOMOTIVE_001"]
ONTOLOGICAL_ISSUES = ["OI_AUTOMOTIVE_001"]
