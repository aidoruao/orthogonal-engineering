"""D_PATTERN_RECOGNITION domain definition — Pattern Recognition

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PATTERN_RECOGNITION"
DOMAIN_NAME = "Pattern Recognition"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['arc-agi', 'grids', 'compositional-rules', 'conditional-inference']
INVARIANTS = ['Grid transformations remain deterministic and proof-carrying.', 'Conditional rule inference is explicit and verifiable.']
FALSIFICATION_TESTS = ["F_PATTERN_RECOGNITION_001"]
ONTOLOGICAL_ISSUES = ["OI_PATTERN_RECOGNITION_001"]
