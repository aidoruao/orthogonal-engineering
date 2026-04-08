"""D_ADMINISTRATIVE_LAW domain definition — Administrative Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ADMINISTRATIVE_LAW"
DOMAIN_NAME = "Administrative Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['apa', 'notice-and-comment', 'chevron', 'arbitrary-capricious']
INVARIANTS = ['Agency rulemaking follows APA notice-and-comment procedure.', 'Chevron deference has bounds; ambiguous statutes require reasoned interpretation.', 'Arbitrary/capricious standard: action must be reasoned and documented.']
FALSIFICATION_TESTS = ["F_ADMINISTRATIVE_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_ADMINISTRATIVE_LAW_001"]
