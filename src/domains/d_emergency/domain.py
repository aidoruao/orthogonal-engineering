"""D_EMERGENCYRESPONSE domain definition — Emergency Response

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_EMERGENCYRESPONSE"
DOMAIN_NAME = "Emergency Response"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['911-dispatch', 'disaster-response', 'mass-notification']

INVARIANTS = ['Dispatch systems handle network partitions without data loss.', 'Mass-notification delivery is confirmed end-to-end within SLO.', 'Emergency systems operate in degraded mode when dependencies are unavailable.']

FALSIFICATION_TESTS = ["F_EMERGENCYRESPONSE_001"]
ONTOLOGICAL_ISSUES = ["OI_EMERGENCYRESPONSE_001"]
