"""D_CORPORATE_LAW domain definition — Corporate Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CORPORATE_LAW"
DOMAIN_NAME = "Corporate Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['fiduciary-duty', 'self-dealing', 'corporate-veil']
INVARIANTS = ['Officers owe fiduciary duty to shareholders (care and loyalty).', 'No self-dealing without full disclosure and approval.', 'Corporate veil pierced only under specific enumerated conditions.']
FALSIFICATION_TESTS = ["F_CORPORATE_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_CORPORATE_LAW_001"]
