"""D_NEIGHBORHOOD_EQUITY domain definition — Neighborhood Resource Equity

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_NEIGHBORHOOD_EQUITY"
DOMAIN_NAME = "Neighborhood Resource Equity"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['resource-allocation', 'investment-disparity', 'redlining-legacy']
INVARIANTS = ['Resource allocation variance across neighborhoods ≤ equity threshold.', 'Investment disparity detection algorithm produces reproducible results.', 'Redlining legacy impact score is documented.']
FALSIFICATION_TESTS = ["F_NEIGHBORHOOEQUITY_001"]
ONTOLOGICAL_ISSUES = ["OI_NEIGHBORHOOEQUITY_001"]
