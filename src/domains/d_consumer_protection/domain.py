"""D_CONSUMER_PROTECTION domain definition — Consumer Protection

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CONSUMER_PROTECTION"
DOMAIN_NAME = "Consumer Protection"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['ftc-act', 'tila', 'truth-in-lending', 'warranty']
INVARIANTS = ['Truth in lending disclosures are complete and accurate.', 'Warranty terms are non-deceptive and enforceable.', 'Recall process is deterministic given defect reports.']
FALSIFICATION_TESTS = ["F_CONSUMER_PROTECTION_001"]
ONTOLOGICAL_ISSUES = ["OI_CONSUMER_PROTECTION_001"]
