"""D_USE_OF_FORCE implementation — Law enforcement use of force.

Covers: necessity, proportionality, de-escalation, accountability,
less-lethal options, deadly force restrictions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from fractions import Fraction
from datetime import datetime


class ForceLevel(Enum):
    VERBAL = "verbal"
    PHYSICAL_RESTRAINT = "physical_restraint"
    LESS_LETHAL = "less_lethal"
    DEADLY_FORCE = "deadly_force"


class ThreatLevel(Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    IMMINENT_DEATH = "imminent_death"


@dataclass
class UseOfForceIncident:
    incident_id: str
    timestamp: datetime
    force_used: ForceLevel
    threat_level: ThreatLevel
    de_escalation_attempted: bool
    subject_injured: bool
    officer_id: str
    justification: str


@dataclass
class ForcePolicy:
    policy_id: str
    jurisdiction: str
    requires_de_escalation: bool
    prohibits_chokeholds: bool
    requires_imminent_threat_for_deadly_force: bool


@dataclass
class D_USE_OF_FORCERecord:
    record_id: str
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    incidents: List[UseOfForceIncident] = field(default_factory=list)


class D_USE_OF_FORCEChecker:
    """Use of force compliance checker."""
    
    def check_compliance(self, record: D_USE_OF_FORCERecord) -> Dict[str, Any]:
        return {
            "compliant": record.status == "active",
            "record_id": record.record_id,
            "incident_count": len(record.incidents),
        }
    
    def check_proportionality(self, incident: UseOfForceIncident) -> bool:
        """Check if force level was proportional to threat."""
        proportional = {
            ThreatLevel.NONE: [ForceLevel.VERBAL],
            ThreatLevel.LOW: [ForceLevel.VERBAL, ForceLevel.PHYSICAL_RESTRAINT],
            ThreatLevel.MODERATE: [ForceLevel.PHYSICAL_RESTRAINT, ForceLevel.LESS_LETHAL],
            ThreatLevel.HIGH: [ForceLevel.LESS_LETHAL, ForceLevel.DEADLY_FORCE],
            ThreatLevel.IMMINENT_DEATH: [ForceLevel.DEADLY_FORCE],
        }
        allowed = proportional.get(incident.threat_level, [])
        return incident.force_used in allowed
    
    def check_necessity(self, incident: UseOfForceIncident, 
                        policy: ForcePolicy) -> bool:
        """Check if force was necessary."""
        if incident.force_used == ForceLevel.DEADLY_FORCE:
            return policy.requires_imminent_threat_for_deadly_force and \
                   incident.threat_level == ThreatLevel.IMMINENT_DEATH
        return True
    
    def check_de_escalation(self, incident: UseOfForceIncident, 
                           policy: ForcePolicy) -> bool:
        """Check if de-escalation was attempted when required."""
        if policy.requires_de_escalation and incident.force_used in [
            ForceLevel.PHYSICAL_RESTRAINT, ForceLevel.LESS_LETHAL, ForceLevel.DEADLY_FORCE
        ]:
            return incident.de_escalation_attempted
        return True
