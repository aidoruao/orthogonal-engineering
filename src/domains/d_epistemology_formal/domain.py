"""D_EPISTEMOLOGY_FORMAL domain definition — Formal Epistemology

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_EPISTEMOLOGY_FORMAL"
DOMAIN_NAME = "Formal Epistemology"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Formal Epistemology routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_EPISTEMOLOGY_FORMAL_001"]
ONTOLOGICAL_ISSUES = ["OI_EPISTEMOLOGY_FORMAL_001"]
