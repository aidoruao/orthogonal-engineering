"""D_METROLOGY domain definition — Metrology

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_METROLOGY"
DOMAIN_NAME = "Metrology"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Metrology routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_METROLOGY_001"]
ONTOLOGICAL_ISSUES = ["OI_METROLOGY_001"]
