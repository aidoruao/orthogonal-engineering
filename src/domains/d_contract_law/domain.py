"""D_CONTRACT_LAW domain definition — Contract Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CONTRACT_LAW"
DOMAIN_NAME = "Contract Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['offer', 'acceptance', 'consideration', 'statute-of-frauds']
INVARIANTS = ['Offer + Acceptance + Consideration = enforceable contract.', 'Statute of frauds requirements enforced for covered contracts.', 'Unconscionability is bounded and documented.']
FALSIFICATION_TESTS = ["F_CONTRACT_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_CONTRACT_LAW_001"]
