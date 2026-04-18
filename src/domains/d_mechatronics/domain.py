"""D_MECHATRONICS domain definition — Mechatronics

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MECHATRONICS"
DOMAIN_NAME = "Mechatronics"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Mechatronics routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_MECHATRONICS_001"]
ONTOLOGICAL_ISSUES = ["OI_MECHATRONICS_001"]
