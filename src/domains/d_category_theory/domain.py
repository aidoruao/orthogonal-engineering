"""D_CATEGORY_THEORY domain definition — Category Theory

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CATEGORY_THEORY"
DOMAIN_NAME = "Category Theory"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Category Theory routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_CATEGORY_THEORY_001"]
ONTOLOGICAL_ISSUES = ["OI_CATEGORY_THEORY_001"]
