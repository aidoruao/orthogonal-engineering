"""D_LEGAL domain definition — Legal

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_LEGAL"
DOMAIN_NAME = "Legal"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['document-management', 'e-discovery', 'compliance']
INVARIANTS = ['Document integrity preserved through pipeline.', 'Audit trail is append-only.']
FALSIFICATION_TESTS = ["F_LEGAL_001"]
ONTOLOGICAL_ISSUES = ["OI_LEGAL_001"]
