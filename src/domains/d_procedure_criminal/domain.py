"""D_PROCEDURE_CRIMINAL domain definition — Criminal Procedure

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PROCEDURE_CRIMINAL"
DOMAIN_NAME = "Criminal Procedure"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['miranda', 'probable-cause', 'speedy-trial', '4th-amendment']
INVARIANTS = ['Miranda warnings required before custodial interrogation.', 'Probable cause required for arrest and search (4th Amendment).', 'Speedy trial clock: trial within statutory period minus excludable days.']
FALSIFICATION_TESTS = ["F_PROCEDURE_CRIMINAL_001"]
ONTOLOGICAL_ISSUES = ["OI_PROCEDURE_CRIMINAL_001"]
