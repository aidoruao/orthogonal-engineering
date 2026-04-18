"""D_LOGIC_FORMAL domain definition — Formal Logic

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_LOGIC_FORMAL"
DOMAIN_NAME = "Formal Logic"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Formal Logic routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_LOGIC_FORMAL_001"]
ONTOLOGICAL_ISSUES = ["OI_LOGIC_FORMAL_001"]
