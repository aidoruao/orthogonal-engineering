"""D_PROBABILITY_THEORY domain definition — Probability Theory

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PROBABILITY_THEORY"
DOMAIN_NAME = "Probability Theory"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Probability Theory routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_PROBABILITY_THEORY_001"]
ONTOLOGICAL_ISSUES = ["OI_PROBABILITY_THEORY_001"]
