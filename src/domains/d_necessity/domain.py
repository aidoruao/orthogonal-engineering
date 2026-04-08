"""D_NECESSITY domain definition — Necessity / Infrastructure

Layer: 4
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_NECESSITY"
DOMAIN_NAME = "Necessity / Infrastructure"
LAYER = 4  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['power-grid', 'water-treatment', 'telecom', 'food-supply']
INVARIANTS = ['All control-system software meets IEC 61508 SIL requirements.', 'No single point of failure in critical control paths.', 'Security patches are applied within the certified maintenance window.']
FALSIFICATION_TESTS = ["F_NECESSITY_001"]
ONTOLOGICAL_ISSUES = ["OI_NECESSITY_001"]
