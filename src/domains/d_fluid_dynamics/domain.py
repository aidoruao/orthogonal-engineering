"""D_FLUID_DYNAMICS domain definition — Fluid Dynamics

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FLUID_DYNAMICS"
DOMAIN_NAME = "Fluid Dynamics"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Fluid Dynamics routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_FLUID_DYNAMICS_001"]
ONTOLOGICAL_ISSUES = ["OI_FLUID_DYNAMICS_001"]
