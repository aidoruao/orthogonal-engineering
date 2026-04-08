"""D_PHARMA domain definition — Pharmaceuticals

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PHARMA"
DOMAIN_NAME = "Pharmaceuticals"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['GMP', 'batch-records', 'cold-chain']
INVARIANTS = ['Batch record is immutable once released.', 'Cold-chain temperature never exceeds spec.']
FALSIFICATION_TESTS = ["F_PHARMA_001"]
ONTOLOGICAL_ISSUES = ["OI_PHARMA_001"]
