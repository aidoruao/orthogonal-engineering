"""D_ABSTRACT_ALGEBRA domain definition — Abstract Algebra

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ABSTRACT_ALGEBRA"
DOMAIN_NAME = "Abstract Algebra"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Abstract Algebra routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_ABSTRACT_ALGEBRA_001"]
ONTOLOGICAL_ISSUES = ["OI_ABSTRACT_ALGEBRA_001"]
