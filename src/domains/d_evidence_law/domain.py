"""D_EVIDENCE_LAW domain definition — Evidence Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_EVIDENCE_LAW"
DOMAIN_NAME = "Evidence Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['hearsay', 'chain-of-custody', 'daubert', 'expert-testimony']
INVARIANTS = ['Hearsay excluded unless enumerated exception applies.', 'Chain of custody is hash-anchored and verified.', 'Expert testimony meets Daubert standard (reliable, relevant).']
FALSIFICATION_TESTS = ["F_EVIDENCE_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_EVIDENCE_LAW_001"]
