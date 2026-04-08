"""D_MINING domain definition — Mining

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MINING"
DOMAIN_NAME = "Mining"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['gas-detection', 'equipment-health', 'evacuation']
INVARIANTS = ['Gas sensor alarms at 20% LEL.', 'Evacuation alarm audible in all zones.']
FALSIFICATION_TESTS = ["F_MINING_001"]
ONTOLOGICAL_ISSUES = ["OI_MINING_001"]
