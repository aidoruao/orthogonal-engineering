"""D_DIPLOMATIC domain definition — Diplomatic Law

Layer: 0
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_DIPLOMATIC"
DOMAIN_NAME = "Diplomatic Law"
LAYER = 0
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['vienna-convention', 'immunity', 'persona-non-grata']
INVARIANTS = ['Diplomatic immunity is bounded by Vienna Convention scope.', 'Persona non grata process is logged with cause and timestamp.']
FALSIFICATION_TESTS = ["F_DIPLOMATIC_001"]
ONTOLOGICAL_ISSUES = ["OI_DIPLOMATIC_001"]
