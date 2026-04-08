"""D_ROAD_STANDARDS domain definition — Road Standards

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: MUTCD, AASHTO Green Book, state DOT standards
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ROAD_STANDARDS"
DOMAIN_NAME = "Road Standards"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "speed-limit",
    "signal-timing",
    "maintenance"
]

INVARIANTS = [
    "Speed limit is deterministic per road classification.",
    "Signal timing is reproducible for given traffic conditions.",
    "Maintenance schedule is logged and executed."
]

FALSIFICATION_TESTS = ["F_ROAD_STANDARDS_001"]
ONTOLOGICAL_ISSUES = ["OI_ROAD_STANDARDS_001"]
