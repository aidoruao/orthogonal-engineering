"""D_ASTROPHYSICS domain definition — Astrophysics

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ASTROPHYSICS"
DOMAIN_NAME = "Astrophysics"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Astrophysics routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_ASTROPHYSICS_001"]
ONTOLOGICAL_ISSUES = ["OI_ASTROPHYSICS_001"]
