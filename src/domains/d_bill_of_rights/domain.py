"""D_BILL_OF_RIGHTS domain definition — Fundamental Rights

Layer: 1
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BILL_OF_RIGHTS"
DOMAIN_NAME = "Fundamental Rights"
LAYER = 1
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['amendments', 'free-speech', 'due-process', 'search-seizure']
INVARIANTS = ['No law shall abridge freedom of speech (1st Amendment).', 'No unreasonable search/seizure without warrant (4th Amendment).', 'Due process before deprivation of life/liberty/property (5th/14th Amendment).']
FALSIFICATION_TESTS = ["F_BILL_OF_RIGHTS_001"]
ONTOLOGICAL_ISSUES = ["OI_BILL_OF_RIGHTS_001"]
