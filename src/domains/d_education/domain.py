"""D_EDUCATION domain definition — Education

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_EDUCATION"
DOMAIN_NAME = "Education"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['LMS', 'proctoring', 'credentials']

INVARIANTS = ['Proctoring detects tab-switch.', 'Credential hash is tamper-evident.']

FALSIFICATION_TESTS = ["F_EDUCATION_001"]
ONTOLOGICAL_ISSUES = ["OI_EDUCATION_001"]
