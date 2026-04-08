"""D_CHEMICAL domain definition — Chemical

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CHEMICAL"
DOMAIN_NAME = "Chemical"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['reactor-control', 'process-safety', 'hazmat']
INVARIANTS = ['Thermal runaway interlock activates before T_critical.', 'Hazmat containment is leak-free.']
FALSIFICATION_TESTS = ["F_CHEMICAL_001"]
ONTOLOGICAL_ISSUES = ["OI_CHEMICAL_001"]
