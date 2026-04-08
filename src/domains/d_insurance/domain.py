"""D_INSURANCE domain definition — Insurance

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_INSURANCE"
DOMAIN_NAME = "Insurance"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['actuarial', 'claims', 'risk-scoring']
INVARIANTS = ['Risk model is deterministic.', 'Claims processing is idempotent.']
FALSIFICATION_TESTS = ["F_INSURANCE_001"]
ONTOLOGICAL_ISSUES = ["OI_INSURANCE_001"]
