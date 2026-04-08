"""D_GAMEMODS domain definition — Video Game Mods

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GAMEMODS"
DOMAIN_NAME = "Video Game Mods"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['ASI-loader', 'DLL-injection', 'version-identity', 'mod-conflict']
INVARIANTS = ['Only one ASI loader occupies the loader interception slot at runtime.', 'Mod version identity is deterministically verifiable against the game executable hash.', 'Conflicting mods are detected and reported before launch.']
FALSIFICATION_TESTS = ["F_GAMEMODS_001"]
ONTOLOGICAL_ISSUES = ["OI_GAMEMODS_001"]
