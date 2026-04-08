"""D_CRIMINAL_LAW domain definition — Criminal Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CRIMINAL_LAW"
DOMAIN_NAME = "Criminal Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['nullum-crimen', 'burden-of-proof', 'sentencing']
INVARIANTS = ['No punishment without prior law (nullum crimen sine lege).', 'Burden of proof is on prosecution; guilt beyond reasonable doubt.', 'Sentencing is within statutory range for offense class.']
FALSIFICATION_TESTS = ["F_CRIMINAL_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_CRIMINAL_LAW_001"]
