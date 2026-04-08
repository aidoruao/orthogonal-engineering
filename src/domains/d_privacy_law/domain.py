"""D_PRIVACY_LAW domain definition — Privacy & Data Protection

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PRIVACY_LAW"
DOMAIN_NAME = "Privacy & Data Protection"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['ccpa', 'hipaa', 'ferpa', 'consent', 'breach-notification']
INVARIANTS = ['PII collection requires documented consent.', 'Data breach notification within statutory window (e.g., 72 hours).', 'Right to deletion: data erased upon verified request.']
FALSIFICATION_TESTS = ["F_PRIVACY_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_PRIVACY_LAW_001"]
