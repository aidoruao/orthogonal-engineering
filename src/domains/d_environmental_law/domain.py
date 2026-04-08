"""D_ENVIRONMENTAL_LAW domain definition — Environmental Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ENVIRONMENTAL_LAW"
DOMAIN_NAME = "Environmental Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['clean-air-act', 'clean-water-act', 'eis', 'polluter-pays']
INVARIANTS = ['Emission limits are deterministic given source type and pollutant.', 'Environmental Impact Statement required before major federal action.', 'Polluter pays principle: cost of cleanup borne by responsible party.']
FALSIFICATION_TESTS = ["F_ENVIRONMENTAL_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_ENVIRONMENTAL_LAW_001"]
