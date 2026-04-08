"""D_COMPUTABILITY domain definition — Computability

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_COMPUTABILITY"
DOMAIN_NAME = "Computability"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['halting', 'rice', 'incompleteness', 'busy-beaver']
INVARIANTS = ['Computability claims are represented as explicit proof objects.', 'Known busy-beaver bounds remain deterministic.']
FALSIFICATION_TESTS = ["F_COMPUTABILITY_001"]
ONTOLOGICAL_ISSUES = ["OI_COMPUTABILITY_001"]
