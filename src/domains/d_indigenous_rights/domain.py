"""D_INDIGENOUS_RIGHTS domain definition — Indigenous Rights

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_INDIGENOUS_RIGHTS"
DOMAIN_NAME = "Indigenous Rights"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['treaty-obligations', 'tribal-sovereignty', 'icwa']
INVARIANTS = ['Treaty obligations to tribal nations are honored.', 'Tribal sovereignty is recognized and respected.', 'ICWA placement preferences are followed.']
FALSIFICATION_TESTS = ["F_INDIGENOUS_RIGHTS_001"]
ONTOLOGICAL_ISSUES = ["OI_INDIGENOUS_RIGHTS_001"]
