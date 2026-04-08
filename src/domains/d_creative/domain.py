"""D_CREATIVE domain definition — Creative / Generative

Layer: 4
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CREATIVE"
DOMAIN_NAME = "Creative / Generative"
LAYER = 4  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['AI-art', 'procedural-generation', 'music-synthesis']
INVARIANTS = ['Given a fixed seed, generative output is reproducible.', 'Style transfer preserves specified content invariants.', 'Generated audio is not perceptually identical to copyrighted material.']
FALSIFICATION_TESTS = ["F_CREATIVE_001"]
ONTOLOGICAL_ISSUES = ["OI_CREATIVE_001"]
