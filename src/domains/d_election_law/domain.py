"""D_ELECTION_LAW domain definition — Election Administration

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ELECTION_LAW"
DOMAIN_NAME = "Election Administration"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['hava', 'feca', 'ballot-design', 'recount']
INVARIANTS = ['Ballot design is deterministic given office and candidates.', 'Recount triggers are formulaic (e.g., margin < 0.5%).', 'Campaign finance limits are enforced with documented compliance.']
FALSIFICATION_TESTS = ["F_ELECTION_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_ELECTION_LAW_001"]
