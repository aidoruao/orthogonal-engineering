"""D_RELIGIOUS_LIBERTY domain definition — Religious Liberty

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_RELIGIOUS_LIBERTY"
DOMAIN_NAME = "Religious Liberty"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['establishment-clause', 'free-exercise', 'rfra']
INVARIANTS = ['Establishment Clause: no state religion or religious preference.', 'Free Exercise: no substantial burden without compelling interest.', 'RFRA strict scrutiny applied where applicable.']
FALSIFICATION_TESTS = ["F_RELIGIOUS_LIBERTY_001"]
ONTOLOGICAL_ISSUES = ["OI_RELIGIOUS_LIBERTY_001"]
