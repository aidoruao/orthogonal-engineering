"""D_HEALTHCARE_LAW domain definition — Healthcare Law & Policy

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_HEALTHCARE_LAW"
DOMAIN_NAME = "Healthcare Law & Policy"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['aca', 'hipaa', 'fda', 'preexisting-conditions']
INVARIANTS = ['Insurance coverage minimums are enforced.', 'Pre-existing condition protection: no denial based on medical history.', 'Drug approval process is documented and reproducible.']
FALSIFICATION_TESTS = ["F_HEALTHCARE_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_HEALTHCARE_LAW_001"]
