"""D_POLITICAL_PHILOSOPHY domain definition — Political Philosophy

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_POLITICAL_PHILOSOPHY"
DOMAIN_NAME = "Political Philosophy"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Political Philosophy routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_POLITICAL_PHILOSOPHY_001"]
ONTOLOGICAL_ISSUES = ["OI_POLITICAL_PHILOSOPHY_001"]
