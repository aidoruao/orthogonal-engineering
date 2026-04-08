"""D_CHILDWELFARE domain definition — Child Welfare

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CHILDWELFARE"
DOMAIN_NAME = "Child Welfare"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['mandatory-reporting', 'investigation', 'foster-care']
INVARIANTS = ['Mandatory reporting requirements enforced.', 'Investigation timeline is bounded by statute.', 'Foster care placement criteria are documented.']
FALSIFICATION_TESTS = ["F_CHILDWELFARE_001"]
ONTOLOGICAL_ISSUES = ["OI_CHILDWELFARE_001"]
