"""D_WHITECOLLAR domain definition — White-Collar / Knowledge Work

Layer: 4
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_WHITECOLLAR"
DOMAIN_NAME = "White-Collar / Knowledge Work"
LAYER = 4  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['compliance', 'audit-trail', 'document-pipeline', 'financial-software']
INVARIANTS = ['Document processing pipelines are idempotent.', 'Audit trails are append-only and cryptographically signed.', 'Financial calculations use arbitrary-precision arithmetic, not floating-point.']
FALSIFICATION_TESTS = ["F_WHITECOLLAR_001"]
ONTOLOGICAL_ISSUES = ["OI_WHITECOLLAR_001"]
