"""D_MANUFACTURING domain definition — Manufacturing

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MANUFACTURING"
DOMAIN_NAME = "Manufacturing"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Manufacturing routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_MANUFACTURING_001"]
ONTOLOGICAL_ISSUES = ["OI_MANUFACTURING_001"]
