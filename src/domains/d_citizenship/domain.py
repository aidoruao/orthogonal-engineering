"""D_CITIZENSHIP domain definition — Citizenship & Naturalization

Layer: 1
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CITIZENSHIP"
DOMAIN_NAME = "Citizenship & Naturalization"
LAYER = 1
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['14th-amendment', 'birthright', 'naturalization', 'due-process']
INVARIANTS = ['Birthright citizenship for those born on US soil (14A §1).', 'Naturalization process is deterministic; no denaturalization without due process.']
FALSIFICATION_TESTS = ["F_CITIZENSHIP_001"]
ONTOLOGICAL_ISSUES = ["OI_CITIZENSHIP_001"]
