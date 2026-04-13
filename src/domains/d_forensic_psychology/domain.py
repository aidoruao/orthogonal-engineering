"""D_FORENSIC_PSYCHOLOGY domain definition — Forensic Psychology & Competency Evaluation.

Layer: 4
CardinalStrength: PREDICATIVE

Dusky competency, Daubert admissibility, civil commitment, and actuarial risk
assessment requirements under U.S. case law and APA Specialty Guidelines.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_FORENSIC_PSYCHOLOGY"
DOMAIN_NAME = "Forensic Psychology & Competency Evaluation — Daubert/Dusky Standards"
LAYER = 4  # Application
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "competency-evaluation",
    "expert-testimony",
    "civil-commitment",
    "risk-assessment",
    "ethical-standards",
]

INVARIANTS = [
    "Defendants must understand charges and be able to assist counsel to be competent to stand trial.",
    "Expert testimony methodology must satisfy Daubert admissibility factors (peer review, testability, error rate, acceptance).",
    "Forensic evaluators must be licensed and board-certified for competency evaluations.",
    "Civil commitment orders require periodic review within maximum allowable intervals.",
    "Actuarial risk assessment instruments must meet minimum AUC and inter-rater reliability thresholds.",
    "Civil commitment is only permissible when danger criteria are met and the least restrictive alternative is applied.",
]

FALSIFICATION_TESTS = [
    "F_FPSY_001",
    "F_FPSY_002",
    "F_FPSY_003",
    "F_FPSY_004",
    "F_FPSY_005",
    "F_FPSY_006",
]
