"""D_UTILITYREGULATION domain definition — Utility Regulation

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_UTILITYREGULATION"
DOMAIN_NAME = "Utility Regulation"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['rate-setting', 'disconnection', 'universal-service']

INVARIANTS = ['Rate-setting formula is deterministic.', 'Service disconnection requires documented notice.', 'Universal service obligation: coverage in all areas.']

FALSIFICATION_TESTS = ["F_UTILITYREGULATION_001"]
ONTOLOGICAL_ISSUES = ["OI_UTILITYREGULATION_001"]
