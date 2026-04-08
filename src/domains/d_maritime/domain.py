"""D_MARITIME domain definition — Maritime

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MARITIME"
DOMAIN_NAME = "Maritime"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['AIS', 'navigation', 'IMO-2021-cyber']
INVARIANTS = ['AIS position within 10m of ground truth.', 'ECDIS chart data is authenticated.']
FALSIFICATION_TESTS = ["F_MARITIME_001"]
ONTOLOGICAL_ISSUES = ["OI_MARITIME_001"]
