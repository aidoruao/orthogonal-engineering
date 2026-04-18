"""D_ARCHITECTURE_DESIGN domain definition — Architecture Design

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARCHITECTURE_DESIGN"
DOMAIN_NAME = "Architecture Design"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Architecture Design routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_ARCHITECTURE_DESIGN_001"]
ONTOLOGICAL_ISSUES = ["OI_ARCHITECTURE_DESIGN_001"]
