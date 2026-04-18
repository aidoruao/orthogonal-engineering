"""D_MUSIC_THEORY domain definition — Music Theory

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MUSIC_THEORY"
DOMAIN_NAME = "Music Theory"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['invariant', 'popperian', 'fraction-only']
INVARIANTS = ['Music Theory routines return deterministic proof objects.', 'All checks use Fraction-only arithmetic.']
FALSIFICATION_TESTS = ["F_MUSIC_THEORY_001"]
ONTOLOGICAL_ISSUES = ["OI_MUSIC_THEORY_001"]
