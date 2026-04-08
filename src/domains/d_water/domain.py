"""D_WATER domain definition — Water and Utilities

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_WATER"
DOMAIN_NAME = "Water and Utilities"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['quality-monitoring', 'distribution', 'SCADA']
INVARIANTS = ['Quality alert fires before limit breach.', 'Isolation valve closes within 10s of command.']
FALSIFICATION_TESTS = ["F_WATER_001"]
ONTOLOGICAL_ISSUES = ["OI_WATER_001"]
