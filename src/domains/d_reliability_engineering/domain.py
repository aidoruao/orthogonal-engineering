"""D_RELIABILITY_ENGINEERING domain definition — Reliability Engineering

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_RELIABILITY_ENGINEERING"
DOMAIN_NAME = "Reliability Engineering"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Reliability Engineering routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_RELIABILITY_ENGINEERING_001"]
ONTOLOGICAL_ISSUES = ["OI_RELIABILITY_ENGINEERING_001"]
