"""D_TRANSIT domain definition — Public Transit

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_TRANSIT"
DOMAIN_NAME = "Public Transit"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['route-planning', 'fare-collection', 'accessibility']
INVARIANTS = ['Transit routes are ADA accessible.', 'Fare collection is auditable.', 'Service frequency meets minimum headway requirements.']
FALSIFICATION_TESTS = ["F_TRANSIT_001"]
ONTOLOGICAL_ISSUES = ["OI_TRANSIT_001"]
