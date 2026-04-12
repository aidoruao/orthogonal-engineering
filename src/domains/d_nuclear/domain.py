"""D_NUCLEAR domain definition — Nuclear Engineering Safety, NRC/IAEA Compliance.

Layer: 4
CardinalStrength: PREDICATIVE

Reactor safety, radiation protection, waste containment, emergency planning,
and criticality safety requirements per NRC and IAEA standards.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_NUCLEAR"
DOMAIN_NAME = "Nuclear Engineering Safety — NRC/IAEA Compliance"
LAYER = 4  # Application
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "reactor-safety",
    "radiation-protection",
    "waste-containment",
    "emergency-planning",
    "criticality-safety",
]

INVARIANTS = [
    "Reactor scram response time must not exceed the design scram limit.",
    "Radiation dose received by workers must remain at or below ALARA target levels.",
    "Reactor containment integrity must be maintained at all times.",
    "Waste container leak rate and storage duration must remain within design bounds.",
    "Emergency notification must be completed within the maximum allowed time.",
    "k-effective must remain strictly subcritical with adequate margin.",
    "At least three independent barriers must be maintained per defense-in-depth principle.",
]

FALSIFICATION_TESTS = [
    "F_NUC_001",
    "F_NUC_002",
    "F_NUC_003",
    "F_NUC_004",
    "F_NUC_005",
    "F_NUC_006",
    "F_NUC_007",
]
