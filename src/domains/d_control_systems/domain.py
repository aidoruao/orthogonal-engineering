"""D_CONTROL_SYSTEMS domain definition — Control Systems

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CONTROL_SYSTEMS"
DOMAIN_NAME = "Control Systems"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Control Systems routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_CONTROL_SYSTEMS_001"]
ONTOLOGICAL_ISSUES = ["OI_CONTROL_SYSTEMS_001"]
