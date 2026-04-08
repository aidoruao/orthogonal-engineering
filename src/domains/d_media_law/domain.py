"""D_MEDIA_LAW domain definition — Media & Press Law

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MEDIA_LAW"
DOMAIN_NAME = "Media & Press Law"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['prior-restraint', 'shield-laws', 'fcc-licensing']
INVARIANTS = ['Prior restraint is presumptively unconstitutional.', 'Shield law protections are enforced.', 'FCC licensing is deterministic and documented.']
FALSIFICATION_TESTS = ["F_MEDIA_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_MEDIA_LAW_001"]
