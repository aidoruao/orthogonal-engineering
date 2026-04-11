"""D_FBI_TRAINING domain definition — Federal Bureau of Investigation Training Standards.

Layer: 4
CardinalStrength: PREDICATIVE

Quantico training, evidence integrity, and use-of-force policy requirements.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FBI_TRAINING"
DOMAIN_NAME = "FBI Training Standards — Quantico Qualification"
LAYER = 4  # Application
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "chain-of-custody",
    "agent-certification",
    "evidence-integrity",
    "use-of-force-policy",
    "witness-verification",
    "digital-forensics",
]

INVARIANTS = [
    "Chain of custody is unbroken and hashes match collection state.",
    "Agent certifications are passing, unexpired, and independently witnessed.",
    "Use of force remains proportional to threat and authorized ratios.",
    "Use-of-force reports include at least two witnesses.",
    "Digital forensic artifacts preserve extraction hash with identified examiner.",
    "Training and certification records are independently witnessed.",
    "Evidence is sealed before transfer when multiple handlers are involved.",
]

FALSIFICATION_TESTS = [
    "F_FBI_001",
    "F_FBI_002",
    "F_FBI_003",
    "F_FBI_004",
    "F_FBI_005",
    "F_FBI_006",
    "F_FBI_007",
]
