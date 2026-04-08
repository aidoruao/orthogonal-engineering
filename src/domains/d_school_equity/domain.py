"""D_SCHOOL_EQUITY domain definition — School Resource Equity

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SCHOOL_EQUITY"
DOMAIN_NAME = "School Resource Equity"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['teacher-quality', 'facility-condition', 'advanced-courses']
INVARIANTS = ['Teacher quality distribution across schools is measured.', 'Facility condition index is documented per school.', 'AP/IB course access equity is measured and reported.']
FALSIFICATION_TESTS = ["F_SCHOOL_EQUITY_001"]
ONTOLOGICAL_ISSUES = ["OI_SCHOOL_EQUITY_001"]
