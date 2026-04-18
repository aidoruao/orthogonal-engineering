"""D_ELECTROMAGNETISM domain definition — Electromagnetism

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ELECTROMAGNETISM"
DOMAIN_NAME = "Electromagnetism"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Electromagnetism routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_ELECTROMAGNETISM_001"]
ONTOLOGICAL_ISSUES = ["OI_ELECTROMAGNETISM_001"]
