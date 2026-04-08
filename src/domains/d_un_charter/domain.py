"""D_UN_CHARTER domain definition — UN Charter & International Law

Layer: 0
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_UN_CHARTER"
DOMAIN_NAME = "UN Charter & International Law"
LAYER = 0
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['jus-cogens', 'human-rights', 'non-derogable']
INVARIANTS = ['No state may violate jus cogens norms (genocide, slavery, torture, piracy).', 'UDHR rights are non-derogable in all circumstances.']
FALSIFICATION_TESTS = ["F_UN_CHARTER_001"]
ONTOLOGICAL_ISSUES = ["OI_UN_CHARTER_001"]
