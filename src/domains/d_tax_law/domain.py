"""D_TAX_LAW domain definition — Tax Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_TAX_LAW"
DOMAIN_NAME = "Tax Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['irc', 'progressive-brackets', 'deductions', 'deterministic']
INVARIANTS = ['Tax liability is deterministic given income and deductions.', 'Progressive brackets are monotonically increasing.', 'No retroactive tax increase; all rates published prospectively.']
FALSIFICATION_TESTS = ["F_TAX_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_TAX_LAW_001"]
