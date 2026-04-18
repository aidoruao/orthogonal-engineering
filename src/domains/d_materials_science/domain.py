"""D_MATERIALS_SCIENCE domain definition — Materials Science

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MATERIALS_SCIENCE"
DOMAIN_NAME = "Materials Science"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Materials Science routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_MATERIALS_SCIENCE_001"]
ONTOLOGICAL_ISSUES = ["OI_MATERIALS_SCIENCE_001"]
