"""D_COMMUNICATIONS domain definition — Communications

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_COMMUNICATIONS"
DOMAIN_NAME = "Communications"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['messaging', 'telecom', 'CDN']
INVARIANTS = ['P99 latency <= 200ms under 10x load.', 'Message ordering is preserved.']
FALSIFICATION_TESTS = ["F_COMMUNICATIONS_001"]
ONTOLOGICAL_ISSUES = ["OI_COMMUNICATIONS_001"]
