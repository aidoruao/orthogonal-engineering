"""D_JUDICIAL_REVIEW domain definition — Judicial Review

Layer: 1
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_JUDICIAL_REVIEW"
DOMAIN_NAME = "Judicial Review"
LAYER = 1
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['marbury', 'constitutional-compliance', 'independent-situs']
INVARIANTS = ['Any statute can be challenged for constitutional compliance.', 'Review is by independent situs (not the enacting branch).']
FALSIFICATION_TESTS = ["F_JUDICIAL_REVIEW_001"]
ONTOLOGICAL_ISSUES = ["OI_JUDICIAL_REVIEW_001"]
