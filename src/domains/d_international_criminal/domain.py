"""D_INTERNATIONAL_CRIMINAL domain definition — International Criminal Law

Layer: 0
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_INTERNATIONAL_CRIMINAL"
DOMAIN_NAME = "International Criminal Law"
LAYER = 0
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['icc', 'universal-jurisdiction', 'complementarity']
INVARIANTS = ['Genocide, war crimes, crimes against humanity have universal jurisdiction.', 'ICC complementarity principle: domestic courts have first priority.']
FALSIFICATION_TESTS = ["F_INTERNATIONAL_CRIMINAL_001"]
ONTOLOGICAL_ISSUES = ["OI_INTERNATIONAL_CRIMINAL_001"]
