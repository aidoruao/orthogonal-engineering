"""D_ECONOMIC_MOBILITY domain definition — Economic Mobility

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ECONOMIC_MOBILITY"
DOMAIN_NAME = "Economic Mobility"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['intergenerational-elasticity', 'opportunity-zones', 'poverty']
INVARIANTS = ['Intergenerational income elasticity is measured consistently.', 'Opportunity zone designation is formulaic.', 'Poverty threshold is deterministic given family size and region.']
FALSIFICATION_TESTS = ["F_ECONOMIC_MOBILITY_001"]
ONTOLOGICAL_ISSUES = ["OI_ECONOMIC_MOBILITY_001"]
