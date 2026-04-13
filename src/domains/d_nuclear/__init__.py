"""D_NUCLEAR domain — Nuclear Engineering Safety, NRC/IAEA Compliance.

Layer: 4 (Application)
CardinalStrength: PREDICATIVE
"""

from .domain import DOMAIN_ID, DOMAIN_NAME, LAYER, CARDINAL_STRENGTH
from .implementation import (
    ReactorUnit,
    RadiationExposure,
    WasteContainer,
    EmergencyPlan,
    CriticalityAssessment,
)
from .invariants import (
    check_scram_response_time,
    check_radiation_dose_alara,
    check_containment_integrity,
    check_waste_containment,
    check_emergency_notification,
    check_criticality_safety,
    check_defense_in_depth,
    run_all_invariants,
)

__all__ = [
    "DOMAIN_ID",
    "DOMAIN_NAME",
    "LAYER",
    "CARDINAL_STRENGTH",
    "ReactorUnit",
    "RadiationExposure",
    "WasteContainer",
    "EmergencyPlan",
    "CriticalityAssessment",
    "check_scram_response_time",
    "check_radiation_dose_alara",
    "check_containment_integrity",
    "check_waste_containment",
    "check_emergency_notification",
    "check_criticality_safety",
    "check_defense_in_depth",
    "run_all_invariants",
]
