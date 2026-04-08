"""D_PROPERTY_LAW domain definition — Property Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PROPERTY_LAW"
DOMAIN_NAME = "Property Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['title', 'adverse-possession', 'eminent-domain', 'just-compensation']
INVARIANTS = ['Title chain is verifiable and hash-anchored.', 'Adverse possession requirements are enumerated (time, open, notorious).', 'Eminent domain requires just compensation (5th Amendment).']
FALSIFICATION_TESTS = ["F_PROPERTY_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_PROPERTY_LAW_001"]
