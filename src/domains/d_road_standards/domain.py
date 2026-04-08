"""D_ROADSTANDARDS domain definition — Road & Highway Standards

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ROADSTANDARDS"
DOMAIN_NAME = "Road & Highway Standards"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['speed-limit', 'signal-timing', 'maintenance']

INVARIANTS = ['Speed limit is deterministic per road classification.', 'Signal timing is reproducible for given traffic conditions.', 'Maintenance schedule is logged and executed.']

FALSIFICATION_TESTS = ["F_ROADSTANDARDS_001"]
ONTOLOGICAL_ISSUES = ["OI_ROADSTANDARDS_001"]
