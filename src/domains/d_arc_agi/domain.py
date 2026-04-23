"""D_ARC_AGI domain definition — ARC-AGI Excedent

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ARC_AGI"
DOMAIN_NAME = "ARC-AGI Excedent"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['benchmark-excedent', 'compositional-generalization', 'novel-rule-transfer', 'exact-match']
INVARIANTS = [
    'ARC-AGI solve rate must be nonzero.',
    'Compositional generalization depth >= 3.',
    'Novel rule transfer rate > 50%.',
    'Grid predictions must match exactly.',
    'No brute-force solutions permitted.',
    'Cross-task transfer rate >= 25%.',
]
FALSIFICATION_TESTS = ["F_ARC_AGI_001"]
ONTOLOGICAL_ISSUES = ["OI_ARC_AGI_001"]
