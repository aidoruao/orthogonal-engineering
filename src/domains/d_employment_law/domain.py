"""D_EMPLOYMENT_LAW domain definition — Employment Law

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_EMPLOYMENT_LAW"
DOMAIN_NAME = "Employment Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['title-vii', 'ada', 'wrongful-termination', 'discrimination']
INVARIANTS = ['At-will termination cannot be based on protected class.', 'ADA reasonable accommodation provided unless undue hardship.', 'Title VII anti-discrimination: hiring/firing/promotion decisions documented.']
FALSIFICATION_TESTS = ["F_EMPLOYMENT_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_EMPLOYMENT_LAW_001"]
