"""D_NUMBER_THEORY domain definition — Number Theory

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_NUMBER_THEORY"
DOMAIN_NAME = "Number Theory"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['modular-arithmetic', 'crt', 'bezout', 'totient']
INVARIANTS = ['Number-theory routines return deterministic proof objects.', 'CRT and Bezout results remain reproducible for identical inputs.']
FALSIFICATION_TESTS = ["F_NUMBER_THEORY_001"]
ONTOLOGICAL_ISSUES = ["OI_NUMBER_THEORY_001"]
