"""D_CURRICULUM domain definition — Curriculum

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State education standards, textbook adoption policies, assessment frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CURRICULUM"
DOMAIN_NAME = "Curriculum"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "state-standards",
    "textbook-adoption",
    "assessment"
]

INVARIANTS = [
    "State standards are enumerated, versioned, and hash-anchored.",
    "Textbook adoption is documented with alignment scores.",
    "Assessment alignment is verifiable against standards."
]

FALSIFICATION_TESTS = ["F_CURRICULUM_001"]
ONTOLOGICAL_ISSUES = ["OI_CURRICULUM_001"]
