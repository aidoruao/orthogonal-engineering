"""D_PUBLICHEALTH domain definition — Public Health Regulation

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: State and federal regulations
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PUBLICHEALTH"
DOMAIN_NAME = "Public Health Regulation"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['vaccination', 'quarantine', 'water-quality']

INVARIANTS = ['Vaccination schedule is evidence-based and versioned.', 'Quarantine authority is bounded by statute.', 'Water fluoridation within EPA limits.']

FALSIFICATION_TESTS = ["F_PUBLICHEALTH_001"]
ONTOLOGICAL_ISSUES = ["OI_PUBLICHEALTH_001"]
