"""D_OCCUPATIONALSAFETY domain definition — Occupational Safety (OSHA)

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_OCCUPATIONALSAFETY"
DOMAIN_NAME = "Occupational Safety (OSHA)"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['hazard-assessment', 'ppe', 'incident-reporting']

INVARIANTS = ['Workplace hazard assessment is documented.', 'PPE requirements are deterministic per hazard class.', 'Incident reporting within statutory window.']

FALSIFICATION_TESTS = ["F_OCCUPATIONALSAFETY_001"]
ONTOLOGICAL_ISSUES = ["OI_OCCUPATIONALSAFETY_001"]
