"""D_ANTITRUST domain definition — Antitrust / Competition

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ANTITRUST"
DOMAIN_NAME = "Antitrust / Competition"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['sherman-act', 'price-fixing', 'merger-review', 'hhi']
INVARIANTS = ['Price-fixing is per se illegal regardless of market power.', 'Merger review threshold is deterministic given market shares.', 'HHI calculation is reproducible and verified.']
FALSIFICATION_TESTS = ["F_ANTITRUST_001"]
ONTOLOGICAL_ISSUES = ["OI_ANTITRUST_001"]
