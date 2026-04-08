"""D_CORPORATE_COMPLIANCE domain definition — Corporate Compliance

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: SEC regulations, EPA reporting, DOL posting requirements
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CORPORATE_COMPLIANCE"
DOMAIN_NAME = "Corporate Compliance"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "annual-filing",
    "environmental-reporting",
    "labor-postings"
]

INVARIANTS = [
    "Annual filing requirements met with documented submission.",
    "Environmental compliance reporting is complete and accurate.",
    "Labor law posting requirements are verified."
]

FALSIFICATION_TESTS = ["F_CORPORATE_COMPLIANCE_001"]
ONTOLOGICAL_ISSUES = ["OI_CORPORATE_COMPLIANCE_001"]
