"""D_LIVECODEBENCH domain definition — LiveCodeBench Excedent

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_LIVECODEBENCH"
DOMAIN_NAME = "LiveCodeBench Excedent"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['benchmark-excedent', 'contamination-free', 'correctness', 'complexity-optimality']
INVARIANTS = [
    'Hard problem rate exceeds 83%.',
    'All problems post-training-cutoff (contamination-free).',
    'Every solved problem must be correct.',
    'Solutions must be asymptotically optimal.',
    'Overall solve rate exceeds 85%.',
]
FALSIFICATION_TESTS = ["F_LIVECODEBENCH_001"]
ONTOLOGICAL_ISSUES = ["OI_LIVECODEBENCH_001"]
