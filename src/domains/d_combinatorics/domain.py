"""D_COMBINATORICS domain definition — Combinatorics

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_COMBINATORICS"
DOMAIN_NAME = "Combinatorics"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['counting', 'catalan', 'pigeonhole', 'inclusion-exclusion']
INVARIANTS = ['Counting identities remain deterministic.', 'Combinatorial proofs stay hash-anchored.']
FALSIFICATION_TESTS = ["F_COMBINATORICS_001"]
ONTOLOGICAL_ISSUES = ["OI_COMBINATORICS_001"]
