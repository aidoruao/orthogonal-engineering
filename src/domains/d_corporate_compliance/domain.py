"""D_CORPORATECOMPLIANCE domain definition — Corporate Regulatory Compliance

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CORPORATECOMPLIANCE"
DOMAIN_NAME = "Corporate Regulatory Compliance"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['annual-filing', 'environmental-reporting', 'labor-postings']

INVARIANTS = ['Annual filing requirements met with documented submission.', 'Environmental compliance reporting is complete and accurate.', 'Labor law posting requirements are verified.']

FALSIFICATION_TESTS = ["F_CORPORATECOMPLIANCE_001"]
ONTOLOGICAL_ISSUES = ["OI_CORPORATECOMPLIANCE_001"]
