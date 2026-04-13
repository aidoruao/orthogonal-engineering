"""D_DIPLOMATIC domain definition — Diplomatic Law.

Layer: 4 (Application)
CardinalStrength: PREDICATIVE

Standards:
- Vienna Convention on Diplomatic Relations (VCDR, 1961)
- Vienna Convention on Consular Relations (VCCR, 1963)
- Diplomatic Relations Act (22 U.S.C. §254a et seq.)
- Convention on Special Missions (1969)
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_DIPLOMATIC"
DOMAIN_NAME = "Diplomatic Law — VCDR/VCCR Compliance"
LAYER = 4
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "vienna-convention",
    "diplomatic-immunity",
    "persona-non-grata",
    "consular-relations",
    "mission-inviolability",
]

INVARIANTS = [
    "Diplomatic agents enjoy personal inviolability; receiving state must not arrest or detain.",
    "Mission premises are inviolable; receiving state may not enter without consent.",
    "Diplomatic agents are immune from criminal and (official) civil jurisdiction.",
    "Persona non grata recall must be completed after declaration by receiving state.",
    "Consular officers enjoy functional immunity for official acts only.",
    "Special mission immunity is limited to the mission duration and official acts.",
]

FALSIFICATION_TESTS = [
    "F_DIPLOMATIC_001",
    "F_DIPLOMATIC_002",
    "F_DIPLOMATIC_003",
    "F_DIPLOMATIC_004",
    "F_DIPLOMATIC_005",
    "F_DIPLOMATIC_006",
]
