"""D_PROCEDURE_CIVIL domain definition — Civil Procedure

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PROCEDURE_CIVIL"
DOMAIN_NAME = "Civil Procedure"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['service-of-process', 'discovery', 'summary-judgment']
INVARIANTS = ['Service of process requirements are met and documented.', 'Discovery scope is bounded by relevance and proportionality.', 'Summary judgment standard is deterministic given pleadings and evidence.']
FALSIFICATION_TESTS = ["F_PROCEDURE_CIVIL_001"]
ONTOLOGICAL_ISSUES = ["OI_PROCEDURE_CIVIL_001"]
