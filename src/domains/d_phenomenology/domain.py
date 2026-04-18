"""D_PHENOMENOLOGY domain definition — Phenomenology

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PHENOMENOLOGY"
DOMAIN_NAME = "Phenomenology"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Phenomenology routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_PHENOMENOLOGY_001"]
ONTOLOGICAL_ISSUES = ["OI_PHENOMENOLOGY_001"]
