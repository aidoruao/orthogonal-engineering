"""D_VETERINARY domain definition — Veterinary Medicine & Animal Welfare.

Layer: 4
CardinalStrength: PREDICATIVE

AWA/USDA compliance, veterinary licensing, drug withdrawal periods,
zoonotic disease reporting, and humane euthanasia requirements.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_VETERINARY"
DOMAIN_NAME = "Veterinary Medicine & Animal Welfare — AWA/USDA Compliance"
LAYER = 4  # Application
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "animal-welfare",
    "veterinary-licensing",
    "drug-withdrawal",
    "zoonotic-reporting",
    "euthanasia",
]

INVARIANTS = [
    "Animal housing facilities provide minimum space per animal as mandated by AWA and 9 CFR Part 3.",
    "Veterinary licenses are active, unexpired, and meet continuing education hour requirements.",
    "Drugs administered to food-producing animals are FDA-CVM approved and withdrawal periods are observed before entry into the food supply.",
    "Reportable zoonotic diseases are reported to authorities within the maximum permissible time window.",
    "Euthanasia employs an AVMA-approved method, is performed by or under a licensed veterinarian, and minimizes pain.",
    "Regulated animal facilities have been inspected within the USDA APHIS-mandated interval.",
]

FALSIFICATION_TESTS = [
    "F_VET_001",
    "F_VET_002",
    "F_VET_003",
    "F_VET_004",
    "F_VET_005",
    "F_VET_006",
]
