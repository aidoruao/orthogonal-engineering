"""D_MEDICALSYSTEMS domain definition — Medical Systems

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MEDICALSYSTEMS"
DOMAIN_NAME = "Medical Systems"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['dosimetry', 'FDA-IEC62304', 'fault-tolerance', 'audit-trail']

INVARIANTS = ['Dosimetry calculations agree with the reference algorithm within certified tolerance.', 'All safety-critical actions are logged with an immutable audit trail.', 'Software failures default to a safe state (fail-safe design).']

FALSIFICATION_TESTS = ["F_MEDICALSYSTEMS_001"]
ONTOLOGICAL_ISSUES = ["OI_MEDICALSYSTEMS_001"]
