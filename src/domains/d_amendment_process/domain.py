"""D_AMENDMENT_PROCESS domain definition — Constitutional Amendment

Layer: 1
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AMENDMENT_PROCESS"
DOMAIN_NAME = "Constitutional Amendment"
LAYER = 1
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['supermajority', 'article-v', 'indelible']
INVARIANTS = ['Amendment requires supermajority: 2/3 Congress + 3/4 states.', 'No amendment can abolish the amendment process itself (Article V).']
FALSIFICATION_TESTS = ["F_AMENDMENT_PROCESS_001"]
ONTOLOGICAL_ISSUES = ["OI_AMENDMENT_PROCESS_001"]
