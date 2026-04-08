"""D_ENVIRONMENTALPLANNING domain definition — Environmental Planning

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ENVIRONMENTALPLANNING"
DOMAIN_NAME = "Environmental Planning"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['wetland', 'endangered-species', 'stormwater']
INVARIANTS = ['Wetland delineation follows Army Corps methodology.', 'Endangered species surveys completed before ground disturbance.', 'Stormwater management meets NPDES permit requirements.']
FALSIFICATION_TESTS = ["F_ENVIRONMENTALPLANNING_001"]
ONTOLOGICAL_ISSUES = ["OI_ENVIRONMENTALPLANNING_001"]
