"""D_FRACTALS domain definition — Fractal Consistency & Self-Similarity

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FRACTALS"
DOMAIN_NAME = "Fractal Consistency & Self-Similarity"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['fractals', 'self-similarity', 'recursive-structures', 'determinism']
INVARIANTS = ['Fractal generation is deterministic: same seed and depth always produce identical output.', 'Self-similarity invariant: each sub-fragment is structurally isomorphic to the whole.', 'Fractal coverage: the generated structure covers the expected proportion of the target space.']
FALSIFICATION_TESTS = ["F_FRACTALS_001"]
ONTOLOGICAL_ISSUES = ["OI_FRACTALS_001"]
