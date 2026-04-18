"""D_GAME_DESIGN domain definition — Game Design

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GAME_DESIGN"
DOMAIN_NAME = "Game Design"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Game Design routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_GAME_DESIGN_001"]
ONTOLOGICAL_ISSUES = ["OI_GAME_DESIGN_001"]
