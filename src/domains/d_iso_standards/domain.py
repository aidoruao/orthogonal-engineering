"""D_ISO_STANDARDS domain definition — International Standards

Layer: 0
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ISO_STANDARDS"
DOMAIN_NAME = "International Standards"
LAYER = 0
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['iso', 'iec', 'pinned-versions']
INVARIANTS = ['Referenced ISO standard version is pinned and hash-anchored.', 'Compliance is binary: a standard is either met or not met.']
FALSIFICATION_TESTS = ["F_ISO_STANDARDS_001"]
ONTOLOGICAL_ISSUES = ["OI_ISO_STANDARDS_001"]
