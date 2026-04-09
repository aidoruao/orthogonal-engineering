"""D_INCIDENT_RESPONSE domain definition — Incident Response

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_INCIDENT_RESPONSE"
DOMAIN_NAME = "Incident Response"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_INCIDENT_RESPONSE_001"]
ONTOLOGICAL_ISSUES = ["OI_D_INCIDENT_RESPONSE_001"]
