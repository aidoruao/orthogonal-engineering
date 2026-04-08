"""D_GEOGRAPHIC_INFORMATION domain definition — Geographic Information Systems

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GEOGRAPHIC_INFORMATION"
DOMAIN_NAME = "Geographic Information Systems"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['boundary-versioning', 'census-tracts', 'gerrymandering']
INVARIANTS = ['Boundary data is versioned and hash-anchored.', 'Census tract mapping is deterministic.', 'Gerrymandering detection (efficiency gap) is reproducible.']
FALSIFICATION_TESTS = ["F_GEOGRAPHIC_INFORMATION_001"]
ONTOLOGICAL_ISSUES = ["OI_GEOGRAPHIC_INFORMATION_001"]
