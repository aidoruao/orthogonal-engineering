"""D_WEBSECURITY domain definition — Web Security

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_WEBSECURITY"
DOMAIN_NAME = "Web Security"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['XSS', 'CSRF', 'injection', 'authentication', 'session-management']

INVARIANTS = ['All user-controlled input is sanitized before reaching an HTML, SQL, or shell sink.', 'Authentication tokens are bound to session and not replayable.', 'CSRF tokens are required for all state-mutating requests.']

FALSIFICATION_TESTS = ["F_WEBSECURITY_001"]
ONTOLOGICAL_ISSUES = ["OI_WEBSECURITY_001"]
