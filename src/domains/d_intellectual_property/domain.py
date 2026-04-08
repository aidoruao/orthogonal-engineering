"""D_INTELLECTUAL_PROPERTY domain definition — Intellectual Property

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_INTELLECTUAL_PROPERTY"
DOMAIN_NAME = "Intellectual Property"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['patent', 'copyright', 'fair-use', 'claims']
INVARIANTS = ['Patent claims are bounded by specification and prosecution history.', 'Copyright duration is deterministic given creation/publication dates.', 'Fair use factors are enumerated and applied consistently.']
FALSIFICATION_TESTS = ["F_INTELLECTUAL_PROPERTY_001"]
ONTOLOGICAL_ISSUES = ["OI_INTELLECTUAL_PROPERTY_001"]
