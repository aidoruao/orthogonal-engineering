"""D_BANKING_REGULATION domain definition — Banking & Finance Regulation

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BANKING_REGULATION"
DOMAIN_NAME = "Banking & Finance Regulation"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['dodd-frank', 'capital-reserves', 'fdic', 'stress-test']
INVARIANTS = ['Capital reserve ratio enforced and continuously monitored.', 'FDIC insurance limit is deterministic per depositor.', 'Stress test results are reproducible for same portfolio.']
FALSIFICATION_TESTS = ["F_BANKING_REGULATION_001"]
ONTOLOGICAL_ISSUES = ["OI_BANKING_REGULATION_001"]
