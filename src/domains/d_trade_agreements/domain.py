"""D_TRADE_AGREEMENTS domain definition — Trade & Commerce Agreements

Layer: 0
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_TRADE_AGREEMENTS"
DOMAIN_NAME = "Trade & Commerce Agreements"
LAYER = 0
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['wto', 'mfn', 'tariffs']
INVARIANTS = ['Tariff schedule is deterministic given product classification.', 'Most-Favored-Nation clause applies uniformly to all parties.']
FALSIFICATION_TESTS = ["F_TRADE_AGREEMENTS_001"]
ONTOLOGICAL_ISSUES = ["OI_TRADE_AGREEMENTS_001"]
