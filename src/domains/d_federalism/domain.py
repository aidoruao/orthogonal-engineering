"""D_FEDERALISM domain definition — Federal/State Structure

Layer: 1
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FEDERALISM"
DOMAIN_NAME = "Federal/State Structure"
LAYER = 1
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['enumerated-powers', 'supremacy-clause', 'residual-powers']
INVARIANTS = ['Enumerated powers are federal; residual powers are state (10th Amendment).', 'Supremacy Clause resolves conflicts: federal > state > local.']
FALSIFICATION_TESTS = ["F_FEDERALISM_001"]
ONTOLOGICAL_ISSUES = ["OI_FEDERALISM_001"]
