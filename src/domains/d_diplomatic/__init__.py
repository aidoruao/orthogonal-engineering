"""D_DIPLOMATIC domain — Diplomatic Law (Vienna Conventions).

Layer: 4 (Application)
CardinalStrength: PREDICATIVE
"""

from .domain import DOMAIN_ID, DOMAIN_NAME, LAYER, CARDINAL_STRENGTH
from .implementation import (
    DiplomaticAgent,
    DiplomaticMission,
    ImmunityWaiver,
    ConsularOfficer,
    SpecialMission,
)
from .invariants import (
    check_diplomatic_inviolability_person,
    check_diplomatic_inviolability_premises,
    check_diplomatic_immunity_jurisdiction,
    check_persona_non_grata_procedure,
    check_consular_functions_immunity,
    check_special_mission_immunity,
    run_all_invariants,
)

__all__ = [
    "DOMAIN_ID",
    "DOMAIN_NAME",
    "LAYER",
    "CARDINAL_STRENGTH",
    "DiplomaticAgent",
    "DiplomaticMission",
    "ImmunityWaiver",
    "ConsularOfficer",
    "SpecialMission",
    "check_diplomatic_inviolability_person",
    "check_diplomatic_inviolability_premises",
    "check_diplomatic_immunity_jurisdiction",
    "check_persona_non_grata_procedure",
    "check_consular_functions_immunity",
    "check_special_mission_immunity",
    "run_all_invariants",
]
