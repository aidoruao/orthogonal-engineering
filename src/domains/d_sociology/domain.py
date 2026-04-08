"""D_SOCIOLOGY domain definition — Sociological Metrics

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE
Source: Professional standards and institutional frameworks
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SOCIOLOGY"
DOMAIN_NAME = "Sociological Metrics"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['gini', 'segregation-index', 'social-mobility']
INVARIANTS = ['Gini coefficient is reproducible for same income distribution.', 'Segregation index (dissimilarity) is deterministic.', 'Social mobility metrics are versioned and documented.']
FALSIFICATION_TESTS = ["F_SOCIOLOGY_001"]
ONTOLOGICAL_ISSUES = ["OI_SOCIOLOGY_001"]
