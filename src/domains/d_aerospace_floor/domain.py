"""D_AEROSPACE_FLOOR domain definition — Aerospace Floor

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AEROSPACE_FLOOR"
DOMAIN_NAME = "Aerospace Floor"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Aerospace Floor routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_AEROSPACE_FLOOR_001"]
ONTOLOGICAL_ISSUES = ["OI_AEROSPACE_FLOOR_001"]
