"""D_BLUECOLLAR domain definition — Blue-Collar / Trades

Layer: 4
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BLUECOLLAR"
DOMAIN_NAME = "Blue-Collar / Trades"
LAYER = 4  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['worker-safety', 'field-service', 'logistics', 'manufacturing']
INVARIANTS = ['Worker safety alerts are delivered within the required response time.', 'Field-service records are immutably logged and tamper-evident.', 'Offline-capable: critical functions work without network connectivity.']
FALSIFICATION_TESTS = ["F_BLUECOLLAR_001"]
ONTOLOGICAL_ISSUES = ["OI_BLUECOLLAR_001"]
