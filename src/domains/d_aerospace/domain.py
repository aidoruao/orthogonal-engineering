"""D_AEROSPACE domain definition — Aerospace

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AEROSPACE"
DOMAIN_NAME = "Aerospace"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['DO-178C', 'avionics', 'structural-health']
INVARIANTS = ['Redundant channels produce byte-identical output.', 'Structural health sensor alerts within spec.']
FALSIFICATION_TESTS = ["F_AEROSPACE_001"]
ONTOLOGICAL_ISSUES = ["OI_AEROSPACE_001"]
