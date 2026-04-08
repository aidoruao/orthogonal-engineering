"""D_LICENSING domain definition — Professional Licensing

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_LICENSING"
DOMAIN_NAME = "Professional Licensing"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['requirements', 'continuing-ed', 'disciplinary']
INVARIANTS = ['License requirements are enumerated per profession.', 'Continuing education tracked and verified.', 'Disciplinary process is documented with due process.']
FALSIFICATION_TESTS = ["F_LICENSING_001"]
ONTOLOGICAL_ISSUES = ["OI_LICENSING_001"]
