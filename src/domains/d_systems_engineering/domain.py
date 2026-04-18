"""D_SYSTEMS_ENGINEERING domain definition — Systems Engineering

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SYSTEMS_ENGINEERING"
DOMAIN_NAME = "Systems Engineering"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Systems Engineering routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_SYSTEMS_ENGINEERING_001"]
ONTOLOGICAL_ISSUES = ["OI_SYSTEMS_ENGINEERING_001"]
