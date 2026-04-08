"""D_SECURITIES_LAW domain definition — Securities Regulation

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SECURITIES_LAW"
DOMAIN_NAME = "Securities Regulation"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['securities-act', 'sec', 'disclosure', 'insider-trading']
INVARIANTS = ['Material information disclosure is mandatory.', 'Insider trading detection is deterministic given trading patterns.', 'Registration requirements are enumerated and enforced.']
FALSIFICATION_TESTS = ["F_SECURITIES_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_SECURITIES_LAW_001"]
