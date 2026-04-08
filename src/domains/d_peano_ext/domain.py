"""D_PEANO_EXT domain definition — Peano Extensions

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PEANO_EXT"
DOMAIN_NAME = "Peano Extensions"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['axioms', 'proof-carrying-arithmetic', 'determinism']
INVARIANTS = ['Extended Peano equalities remain hash-verifiable.', 'Arithmetic identities remain reproducible across runs.']
FALSIFICATION_TESTS = ["F_PEANO_EXT_001"]
ONTOLOGICAL_ISSUES = ["OI_PEANO_EXT_001"]
