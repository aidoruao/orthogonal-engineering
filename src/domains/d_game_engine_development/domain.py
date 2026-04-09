"""D_GAME_ENGINE_DEVELOPMENT domain definition — Game Engine Development

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GAME_ENGINE_DEVELOPMENT"
DOMAIN_NAME = "Game Engine Development"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = []
INVARIANTS = []
FALSIFICATION_TESTS = ["F_D_GAME_ENGINE_DEVELOPMENT_001"]
ONTOLOGICAL_ISSUES = ["OI_D_GAME_ENGINE_DEVELOPMENT_001"]
