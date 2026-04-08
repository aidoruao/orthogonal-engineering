"""D_GAME_THEORY domain definition — Game Theory

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GAME_THEORY"
DOMAIN_NAME = "Game Theory"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['equilibrium', 'minimax', 'mechanism-design']
INVARIANTS = ['Pure equilibrium detection is deterministic.', 'Mechanism checks expose profitable deviations.']
FALSIFICATION_TESTS = ["F_GAME_THEORY_001"]
ONTOLOGICAL_ISSUES = ["OI_GAME_THEORY_001"]
