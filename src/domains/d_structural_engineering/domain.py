"""D_STRUCTURAL_ENGINEERING domain definition — Structural Engineering

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_STRUCTURAL_ENGINEERING"
DOMAIN_NAME = "Structural Engineering"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Structural Engineering routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_STRUCTURAL_ENGINEERING_001"]
ONTOLOGICAL_ISSUES = ["OI_STRUCTURAL_ENGINEERING_001"]
