"""D_DIGITAL_GOVERNANCE domain definition — Digital Governance

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_DIGITAL_GOVERNANCE"
DOMAIN_NAME = "Digital Governance"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['wcag', 'open-data', 'algorithmic-accountability']
INVARIANTS = ['Government digital services meet WCAG 2.1 AA standards.', 'Open data requirements are met.', 'Algorithmic accountability for government AI is enforced.']
FALSIFICATION_TESTS = ["F_DIGITAL_GOVERNANCE_001"]
ONTOLOGICAL_ISSUES = ["OI_DIGITAL_GOVERNANCE_001"]
