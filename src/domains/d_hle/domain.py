"""D_HLE domain definition — Humanity's Last Exam Excedent

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_HLE"
DOMAIN_NAME = "Humanity's Last Exam Excedent"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['benchmark-excedent', 'proof-chain', 'domain-breadth', 'no-memorization']
INVARIANTS = [
    'HLE score exceeds 70%.',
    'Text-only score exceeds 40%.',
    'Every solution has a valid ProofObject chain.',
    'At least 10 domains covered (polymath requirement).',
    'Solutions must show reasoning, not verbatim recall.',
]
FALSIFICATION_TESTS = ["F_HLE_001"]
ONTOLOGICAL_ISSUES = ["OI_HLE_001"]
