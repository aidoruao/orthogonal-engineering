"""D_ELDERCARE domain definition — Elder Care Regulation

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ELDERCARE"
DOMAIN_NAME = "Elder Care Regulation"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['staffing-ratios', 'abuse-reporting', 'medicaid']
INVARIANTS = ['Nursing home staffing ratios enforced.', 'Abuse reporting requirements met.', 'Medicaid eligibility is formulaic and deterministic.']
FALSIFICATION_TESTS = ["F_ELDERCARE_001"]
ONTOLOGICAL_ISSUES = ["OI_ELDERCARE_001"]
