"""D_ENERGY domain definition — Energy

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ENERGY"
DOMAIN_NAME = "Energy"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['smart-grid', 'demand-response', 'renewable']
INVARIANTS = ['DR events actioned within 30s.', 'Grid frequency deviation triggers load shed.']
FALSIFICATION_TESTS = ["F_ENERGY_001"]
ONTOLOGICAL_ISSUES = ["OI_ENERGY_001"]
