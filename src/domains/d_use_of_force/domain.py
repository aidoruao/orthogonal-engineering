"""D_USE_OF_FORCE domain definition — Use of Force Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_USE_OF_FORCE"
DOMAIN_NAME = "Use of Force Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['graham-connor', 'proportionality', 'deadly-force', 'body-cam']
INVARIANTS = ['Force must be proportional to threat (Graham v. Connor).', 'Deadly force only when imminent threat of death/serious injury.', 'All force incidents logged with body cam hash or presumptively unjustified.']
FALSIFICATION_TESTS = ["F_USE_OF_FORCE_001"]
ONTOLOGICAL_ISSUES = ["OI_USE_OF_FORCE_001"]
