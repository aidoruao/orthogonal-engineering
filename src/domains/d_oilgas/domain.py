"""D_OILGAS domain definition — Oil and Gas

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_OILGAS"
DOMAIN_NAME = "Oil and Gas"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['pipeline-SCADA', 'blowout-prevention', 'environmental']
INVARIANTS = ['Leak detected within 60s.', 'BOP closes within spec time.']
FALSIFICATION_TESTS = ["F_OILGAS_001"]
ONTOLOGICAL_ISSUES = ["OI_OILGAS_001"]
