"""D_THERMODYNAMICS domain definition — Thermodynamics

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_THERMODYNAMICS"
DOMAIN_NAME = "Thermodynamics"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Thermodynamics routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_THERMODYNAMICS_001"]
ONTOLOGICAL_ISSUES = ["OI_THERMODYNAMICS_001"]
