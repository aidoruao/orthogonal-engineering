"""D_STATISTICS domain definition — Statistics

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_STATISTICS"
DOMAIN_NAME = "Statistics"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Statistics routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_STATISTICS_001"]
ONTOLOGICAL_ISSUES = ["OI_STATISTICS_001"]
