"""D_AVIATION domain definition — Aviation & ATC

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: 14 CFR (Federal Aviation Regulations), ICAO standards
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AVIATION"
DOMAIN_NAME = "Aviation & ATC"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "flight-management",
    "METAR",
    "external-API",
    "safety-critical-timing"
]

INVARIANTS = [
    "All external API calls have a defined timeout and fallback.",
    "Stale data is flagged to the pilot; no silent data propagation.",
    "Safety-critical computations complete within the certified time budget."
]

FALSIFICATION_TESTS = ["F_AVIATION_004"]
ONTOLOGICAL_ISSUES = ["OI_AVIATION_001"]
