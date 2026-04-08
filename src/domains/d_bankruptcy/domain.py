"""D_BANKRUPTCY domain definition — Bankruptcy

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BANKRUPTCY"
DOMAIN_NAME = "Bankruptcy"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['chapter-7', 'chapter-11', 'means-test', 'automatic-stay']
INVARIANTS = ['Chapter 7/11/13 eligibility is formulaic and deterministic.', 'Means test produces same result for identical inputs.', 'Automatic stay is immediate upon filing.']
FALSIFICATION_TESTS = ["F_BANKRUPTCY_001"]
ONTOLOGICAL_ISSUES = ["OI_BANKRUPTCY_001"]
