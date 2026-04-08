"""D_GAMING domain definition — Gaming

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GAMING"
DOMAIN_NAME = "Gaming"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['multiplayer', 'anti-cheat', 'save-files', 'network-safety']
INVARIANTS = ['Deterministic seed produces identical game state.', 'Network packets cannot trigger memory corruption.', 'Mod sandbox is enforced.']
FALSIFICATION_TESTS = ["F_GAMING_001"]
ONTOLOGICAL_ISSUES = ["OI_GAMING_001"]
