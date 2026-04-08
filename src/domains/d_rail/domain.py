"""D_RAIL domain definition — Rail

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_RAIL"
DOMAIN_NAME = "Rail"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['ETCS', 'signalling', 'PTC', 'IEC-62280']
INVARIANTS = ['PTC halts train before stop signal.', 'Track-circuit occupancy has no false negatives.']
FALSIFICATION_TESTS = ["F_RAIL_001"]
ONTOLOGICAL_ISSUES = ["OI_RAIL_001"]
