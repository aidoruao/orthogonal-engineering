"""D_BIOCHEMISTRY domain definition — Biochemistry

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BIOCHEMISTRY"
DOMAIN_NAME = "Biochemistry"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Biochemistry routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_BIOCHEMISTRY_001"]
ONTOLOGICAL_ISSUES = ["OI_BIOCHEMISTRY_001"]
