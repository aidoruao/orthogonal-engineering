"""D_BORING domain definition — Boring / Commodity

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BORING"
DOMAIN_NAME = "Boring / Commodity"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['CRUD', 'ETL', 'report-generation', 'data-format-conversion']
INVARIANTS = ['ETL pipelines are idempotent: re-running produces the same output.', 'Report generation is deterministic given identical inputs.', 'Data-format conversions preserve all semantic content.']
FALSIFICATION_TESTS = ["F_BORING_001"]
ONTOLOGICAL_ISSUES = ["OI_BORING_001"]
