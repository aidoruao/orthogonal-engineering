"""D_TRANSPORTATION domain definition — Transportation

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_TRANSPORTATION"
DOMAIN_NAME = "Transportation"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['fleet-tracking', 'logistics', 'real-time']
INVARIANTS = ['Fleet GPS accurate within 5m CEP.', 'Route optimization is deterministic.']
FALSIFICATION_TESTS = ["F_TRANSPORTATION_001"]
ONTOLOGICAL_ISSUES = ["OI_TRANSPORTATION_001"]
