"""D_ARC_AGI_3 domain definition — ARC-AGI-3 Solver

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARC_AGI_3"
DOMAIN_NAME = "ARC-AGI-3 Solver"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['arc-agi', 'bounded-dsl', 'symbolic-program-synthesis', 'grid-transformations']
INVARIANTS = ['ARC solver programs are bounded-depth and halt deterministically.', 'Every synthesized ARC program is proof-carrying and verifiable on held-out examples.', 'ARC predictions remain reproducible under identical train/test pairs.']
FALSIFICATION_TESTS = ["F_ARC_AGI_3_001"]
ONTOLOGICAL_ISSUES = ["OI_ARC_AGI_3_001"]
