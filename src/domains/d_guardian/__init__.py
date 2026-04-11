"""D_GUARDIAN domain — Operation T-800 Guardian Agent

Autonomous protective agent domain with ethical constraints.
Layer: 4 (Application)
CardinalStrength: PREDICATIVE

Extends CrusaderCap with solo protector constraint and liveness requirements.
"""

from .domain import DOMAIN_ID, DOMAIN_NAME, LAYER, CARDINAL_STRENGTH
from .implementation import (
    GuardianAgent, GuardianStatus,
    ThreatAssessment, ProtectionRecord,
    GuardianCap,
)
from .invariants import (
    check_solo_protector,
    check_liveness,
    check_proportional_response,
    check_principal_survival,
    check_no_termination_mode,
    check_withdrawal_protocol,
    check_force_witness,
)

__all__ = [
    "DOMAIN_ID",
    "DOMAIN_NAME", 
    "LAYER",
    "CARDINAL_STRENGTH",
    "GuardianAgent",
    "GuardianStatus",
    "ThreatAssessment",
    "ProtectionRecord",
    "GuardianCap",
    "check_solo_protector",
    "check_liveness",
    "check_proportional_response",
    "check_principal_survival",
    "check_no_termination_mode",
    "check_withdrawal_protocol",
    "check_force_witness",
]
