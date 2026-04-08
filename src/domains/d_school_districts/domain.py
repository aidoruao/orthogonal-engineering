"""D_SCHOOLDISTRICTS domain definition — School District Boundaries

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SCHOOLDISTRICTS"
DOMAIN_NAME = "School District Boundaries"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['boundaries', 'gerrymandering', 'compactness']

INVARIANTS = ['District boundary changes require public process and documentation.', 'Boundary gerrymandering detection uses compactness score.', 'Cross-district transfer rules are deterministic.']

FALSIFICATION_TESTS = ["F_SCHOOLDISTRICTS_001"]
ONTOLOGICAL_ISSUES = ["OI_SCHOOLDISTRICTS_001"]
