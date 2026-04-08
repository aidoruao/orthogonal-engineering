"""D_CIVIL_LAW domain definition — Civil Law / Torts

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CIVIL_LAW"
DOMAIN_NAME = "Civil Law / Torts"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['duty', 'breach', 'causation', 'damages']
INVARIANTS = ['Duty → Breach → Causation → Damages chain must be functorial.', 'Statute of limitations is enforced with documented filing date.']
FALSIFICATION_TESTS = ["F_CIVIL_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_CIVIL_LAW_001"]
