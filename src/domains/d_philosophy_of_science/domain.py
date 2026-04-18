"""D_PHILOSOPHY_OF_SCIENCE domain definition — Philosophy of Science

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PHILOSOPHY_OF_SCIENCE"
DOMAIN_NAME = "Philosophy of Science"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Philosophy of Science routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_PHILOSOPHY_OF_SCIENCE_001"]
ONTOLOGICAL_ISSUES = ["OI_PHILOSOPHY_OF_SCIENCE_001"]
