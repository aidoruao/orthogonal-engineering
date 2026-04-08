"""D_POLICEPROCEDURE domain definition — Police Procedure & Accountability

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_POLICEPROCEDURE"
DOMAIN_NAME = "Police Procedure & Accountability"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['body-cam', 'use-of-force-report', 'complaint-process']

INVARIANTS = ['Body cam must be active during all citizen encounters.', 'Use of force report filed within 24 hours.', 'Complaint process is deterministic and documented.']

FALSIFICATION_TESTS = ["F_POLICEPROCEDURE_001"]
ONTOLOGICAL_ISSUES = ["OI_POLICEPROCEDURE_001"]
