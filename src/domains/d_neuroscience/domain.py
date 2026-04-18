"""D_NEUROSCIENCE domain definition — Neuroscience

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_NEUROSCIENCE"
DOMAIN_NAME = "Neuroscience"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Neuroscience routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_NEUROSCIENCE_001"]
ONTOLOGICAL_ISSUES = ["OI_NEUROSCIENCE_001"]
