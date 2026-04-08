"""D_NONCREATIVE domain definition — Non-Creative / Deterministic

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_NONCREATIVE"
DOMAIN_NAME = "Non-Creative / Deterministic"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['batch-processing', 'compression', 'data-format-conversion']
INVARIANTS = ['Compression/decompression is lossless and reproducible.', 'Batch processing output is identical for identical inputs.', 'Format conversion round-trips without data loss.']
FALSIFICATION_TESTS = ["F_NONCREATIVE_001"]
ONTOLOGICAL_ISSUES = ["OI_NONCREATIVE_001"]
