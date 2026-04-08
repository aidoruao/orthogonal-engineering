"""D_CONSTRUCTION domain definition — Construction

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CONSTRUCTION"
DOMAIN_NAME = "Construction"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['BIM', 'structural-analysis', 'site-safety']
INVARIANTS = ['FEM results within 1% of reference.', 'Site safety alerts delivered within SLO.']
FALSIFICATION_TESTS = ["F_CONSTRUCTION_001"]
ONTOLOGICAL_ISSUES = ["OI_CONSTRUCTION_001"]
