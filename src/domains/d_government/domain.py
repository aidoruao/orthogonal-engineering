"""D_GOVERNMENT domain definition — Government

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GOVERNMENT"
DOMAIN_NAME = "Government"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['voting', 'benefits', 'digital-identity']

INVARIANTS = ['Vote is recorded as cast.', 'Identity verification is not forgeable.']

FALSIFICATION_TESTS = ["F_GOVERNMENT_001"]
ONTOLOGICAL_ISSUES = ["OI_GOVERNMENT_001"]
