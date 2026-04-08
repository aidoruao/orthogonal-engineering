"""D_LABOR_RIGHTS domain definition — Labor Rights Enforcement

Layer: 2
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_LABOR_RIGHTS"
DOMAIN_NAME = "Labor Rights Enforcement"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['wage-theft', 'frontloading', 'off-the-clock', 'compliance-extraction', 'documentation-as-defense']
INVARIANTS = ['Any hours worked over 40 in a week must be compensated at 1.5x (FLSA 29 U.S.C. § 207).', 'Assigned workload must be achievable within scheduled hours.', 'No employee may be allowed to work without compensation.', 'Compliance traits must not correlate with unpaid labor extraction.']
FALSIFICATION_TESTS = ["F_LABOR_RIGHTS_001"]
ONTOLOGICAL_ISSUES = ["OI_LABOR_RIGHTS_001"]
