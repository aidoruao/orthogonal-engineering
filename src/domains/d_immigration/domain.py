"""D_IMMIGRATION domain definition — Immigration Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_IMMIGRATION"
DOMAIN_NAME = "Immigration Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['ina', 'visa-categories', 'asylum', 'deportation']
INVARIANTS = ['Visa categories are enumerated; eligibility is deterministic.', 'Asylum claim requires documented persecution on protected grounds.', 'Deportation requires due process (links to D_HABEAS_CORPUS).']
FALSIFICATION_TESTS = ["F_IMMIGRATION_001"]
ONTOLOGICAL_ISSUES = ["OI_IMMIGRATION_001"]
