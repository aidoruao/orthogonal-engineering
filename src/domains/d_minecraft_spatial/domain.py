"""D_MINECRAFT_SPATIAL domain definition — Minecraft Spatial Invariants

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_MINECRAFT_SPATIAL"
DOMAIN_NAME = "Minecraft Spatial Invariants"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['cc-tweaked', 'turtle-constraints', 'sign-parsing', 'gps-dead-reckoning', 'world-state-export', 'pre-action-checking']
INVARIANTS = ['Sign text is parsed correctly from turtle.inspect() data.state fields (MC 1.20+ double-sided signs).', 'GPS dead reckoning position matches GPS trilateration within 1 block after N movements.', 'World state export via anvil-parser produces deterministic JSON for identical .mca region files.', 'Pre-action constraint check rejects any turtle command that violates spatial invariants.']
FALSIFICATION_TESTS = ["F_MINECRAFT_SPATIAL_001"]
ONTOLOGICAL_ISSUES = ["OI_MINECRAFT_SPATIAL_001"]
