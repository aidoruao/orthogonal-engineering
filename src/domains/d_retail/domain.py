"""D_RETAIL domain definition — Retail

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_RETAIL"
DOMAIN_NAME = "Retail"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['POS', 'inventory', 'e-commerce']
INVARIANTS = ['POS transaction is idempotent under retry.', 'Inventory count is consistent across nodes.']
FALSIFICATION_TESTS = ["F_RETAIL_001"]
ONTOLOGICAL_ISSUES = ["OI_RETAIL_001"]
