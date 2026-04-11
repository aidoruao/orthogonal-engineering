"""D_FBI_TRAINING domain — Federal Bureau of Investigation Training Standards

Layer: 4 (Application)
CardinalStrength: PREDICATIVE
"""

from .domain import DOMAIN_ID, DOMAIN_NAME, LAYER, CARDINAL_STRENGTH
from .implementation import (
    EvidenceItem,
    AgentCertification,
    UseOfForceReport,
    DigitalForensicArtifact,
)
from .invariants import (
    check_chain_of_custody,
    check_agent_certification_valid,
    check_use_of_force_proportional,
    check_witness_verification,
    check_digital_forensic_integrity,
    check_training_record_witnessed,
    check_evidence_sealed,
    run_all_invariants,
)

__all__ = [
    "DOMAIN_ID",
    "DOMAIN_NAME",
    "LAYER",
    "CARDINAL_STRENGTH",
    "EvidenceItem",
    "AgentCertification",
    "UseOfForceReport",
    "DigitalForensicArtifact",
    "check_chain_of_custody",
    "check_agent_certification_valid",
    "check_use_of_force_proportional",
    "check_witness_verification",
    "check_digital_forensic_integrity",
    "check_training_record_witnessed",
    "check_evidence_sealed",
    "run_all_invariants",
]
