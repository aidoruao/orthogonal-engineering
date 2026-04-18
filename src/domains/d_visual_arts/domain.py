"""D_VISUAL_ARTS domain definition — Visual Arts

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_VISUAL_ARTS"
DOMAIN_NAME = "Visual Arts"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Visual Arts routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_VISUAL_ARTS_001"]
ONTOLOGICAL_ISSUES = ["OI_VISUAL_ARTS_001"]
