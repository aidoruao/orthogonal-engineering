"""D_HOSPITALITY domain definition — Hospitality

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_HOSPITALITY"
DOMAIN_NAME = "Hospitality"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['reservations', 'room-keys', 'PCI-DSS']
INVARIANTS = ['Room key deactivated within 5s of checkout.', 'PCI data is not logged in plaintext.']
FALSIFICATION_TESTS = ["F_HOSPITALITY_001"]
ONTOLOGICAL_ISSUES = ["OI_HOSPITALITY_001"]
