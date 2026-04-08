"""D_AGRICULTURE domain definition — Agriculture

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AGRICULTURE"
DOMAIN_NAME = "Agriculture"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['precision-farming', 'irrigation', 'livestock']
INVARIANTS = ['Irrigation delivers within +/-10% of setpoint.', 'Pesticide dosing within approved range.']
FALSIFICATION_TESTS = ["F_AGRICULTURE_001"]
ONTOLOGICAL_ISSUES = ["OI_AGRICULTURE_001"]
