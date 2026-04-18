"""D_INFORMATION_THEORY domain definition — Information Theory

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_INFORMATION_THEORY"
DOMAIN_NAME = "Information Theory"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Information Theory routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_INFORMATION_THEORY_001"]
ONTOLOGICAL_ISSUES = ["OI_INFORMATION_THEORY_001"]
