"""D_PSYCHOLOGY domain definition — Clinical Psychology Standards

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PSYCHOLOGY"
DOMAIN_NAME = "Clinical Psychology Standards"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['dsm', 'diagnostic-criteria', 'treatment-protocols']
INVARIANTS = ['DSM diagnostic criteria are versioned and enumerated.', 'Treatment protocols are evidence-based and documented.', 'Informed consent is documented for all interventions.']
FALSIFICATION_TESTS = ["F_PSYCHOLOGY_001"]
ONTOLOGICAL_ISSUES = ["OI_PSYCHOLOGY_001"]
