"""D_DIFFERENTIAL_GEOMETRY domain definition — Differential Geometry

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_DIFFERENTIAL_GEOMETRY"
DOMAIN_NAME = "Differential Geometry"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Differential Geometry routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_DIFFERENTIAL_GEOMETRY_001"]
ONTOLOGICAL_ISSUES = ["OI_DIFFERENTIAL_GEOMETRY_001"]
