"""D_ETHICS domain definition — Ethics Frameworks

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ETHICS"
DOMAIN_NAME = "Ethics Frameworks"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['irb', 'conflict-of-interest', 'whistleblower']
INVARIANTS = ['Ethical review (IRB) process is documented.', 'Conflict of interest disclosure is mandatory.', 'Whistleblower protection is enforced.']
FALSIFICATION_TESTS = ["F_ETHICS_001"]
ONTOLOGICAL_ISSUES = ["OI_ETHICS_001"]
