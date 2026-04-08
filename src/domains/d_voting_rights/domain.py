"""D_VOTING_RIGHTS domain definition — Voting & Elections

Layer: 1
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_VOTING_RIGHTS"
DOMAIN_NAME = "Voting & Elections"
LAYER = 1
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['15th-amendment', '19th-amendment', '26th-amendment', 'no-poll-tax']
INVARIANTS = ['Vote is recorded as cast and verifiable.', 'No racial discrimination in voting (15A, 24A); no sex discrimination (19A).']
FALSIFICATION_TESTS = ["F_VOTING_RIGHTS_001"]
ONTOLOGICAL_ISSUES = ["OI_VOTING_RIGHTS_001"]
