"""D_POLICE_PROCEDURE domain definition — Police Procedure

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: Department policies, state POST standards, consent decrees
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_POLICE_PROCEDURE"
DOMAIN_NAME = "Police Procedure"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "body-cam",
    "use-of-force-report",
    "complaint-process"
]

INVARIANTS = [
    "Body cam must be active during all citizen encounters.",
    "Use of force report filed within 24 hours.",
    "Complaint process is deterministic and documented."
]

FALSIFICATION_TESTS = ["F_POLICE_PROCEDURE_001"]
ONTOLOGICAL_ISSUES = ["OI_POLICE_PROCEDURE_001"]
