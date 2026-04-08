"""D_FUN domain definition — Fun / Entertainment

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FUN"
DOMAIN_NAME = "Fun / Entertainment"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['games', 'interactive-media', 'generative-art']
INVARIANTS = ['Deterministic game seeds produce identical game states.', 'Saved game data is forward-compatible with new versions.', 'Online matchmaking produces fair and deterministic results.']
FALSIFICATION_TESTS = ["F_FUN_001"]
ONTOLOGICAL_ISSUES = ["OI_FUN_001"]
