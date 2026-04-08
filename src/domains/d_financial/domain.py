"""D_FINANCIAL domain definition — Financial

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FINANCIAL"
DOMAIN_NAME = "Financial"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['trading', 'settlement', 'fraud-detection']
INVARIANTS = ['Double-spend is rejected.', 'Settlement is deterministic.']
FALSIFICATION_TESTS = ["F_FINANCIAL_001"]
ONTOLOGICAL_ISSUES = ["OI_FINANCIAL_001"]
