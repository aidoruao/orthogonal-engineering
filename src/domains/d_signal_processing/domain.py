"""D_SIGNAL_PROCESSING domain definition — Signal Processing

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SIGNAL_PROCESSING"
DOMAIN_NAME = "Signal Processing"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Signal Processing routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_SIGNAL_PROCESSING_001"]
ONTOLOGICAL_ISSUES = ["OI_SIGNAL_PROCESSING_001"]
