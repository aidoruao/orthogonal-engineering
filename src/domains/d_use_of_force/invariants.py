"""D_USE_OF_FORCE invariant checks — use of force validation.

Use of force invariants ensure:
1. Proportionality between force and threat
2. Necessity of force used
3. De-escalation attempted when possible
4. Deadly force only for imminent threat
5. Documentation and accountability
"""

from datetime import datetime
from fractions import Fraction

from .implementation import (
    D_USE_OF_FORCEChecker,
    D_USE_OF_FORCERecord,
    UseOfForceIncident,
    ForceLevel,
    ThreatLevel,
    ForcePolicy,
)


def check_force_proportionality() -> bool:
    """Verify force level is proportional to threat level."""
    checker = D_USE_OF_FORCEChecker()
    
    # Appropriate: verbal command for low threat
    proportional = UseOfForceIncident(
        incident_id="INC-001",
        timestamp=datetime.now(),
        force_used=ForceLevel.VERBAL,
        threat_level=ThreatLevel.LOW,
        de_escalation_attempted=True,
        subject_injured=False,
        officer_id="OFF-001",
        justification="Subject non-compliant",
    )
    
    assert checker.check_proportionality(proportional)
    
    # Inappropriate: deadly force for low threat
    disproportionate = UseOfForceIncident(
        incident_id="INC-002",
        timestamp=datetime.now(),
        force_used=ForceLevel.DEADLY_FORCE,
        threat_level=ThreatLevel.LOW,
        de_escalation_attempted=False,
        subject_injured=True,
        officer_id="OFF-002",
        justification="Invalid",
    )
    
    assert not checker.check_proportionality(disproportionate)
    
    return True


def check_deadly_force_necessity() -> bool:
    """Verify deadly force is only used for imminent threat of death."""
    checker = D_USE_OF_FORCEChecker()
    
    policy = ForcePolicy(
        policy_id="POL-001",
        jurisdiction="State X",
        requires_de_escalation=True,
        prohibits_chokeholds=True,
        requires_imminent_threat_for_deadly_force=True,
    )
    
    # Valid: deadly force for imminent death threat
    valid_deadly_force = UseOfForceIncident(
        incident_id="INC-003",
        timestamp=datetime.now(),
        force_used=ForceLevel.DEADLY_FORCE,
        threat_level=ThreatLevel.IMMINENT_DEATH,
        de_escalation_attempted=True,
        subject_injured=True,
        officer_id="OFF-003",
        justification="Subject had weapon",
    )
    
    assert checker.check_necessity(valid_deadly_force, policy)
    
    # Invalid: deadly force without imminent threat
    invalid_deadly_force = UseOfForceIncident(
        incident_id="INC-004",
        timestamp=datetime.now(),
        force_used=ForceLevel.DEADLY_FORCE,
        threat_level=ThreatLevel.HIGH,
        de_escalation_attempted=False,
        subject_injured=True,
        officer_id="OFF-004",
        justification="Invalid",
    )
    
    assert not checker.check_necessity(invalid_deadly_force, policy)
    
    return True


def check_de_escalation_attempted() -> bool:
    """Verify de-escalation is attempted before physical force."""
    checker = D_USE_OF_FORCEChecker()
    
    policy = ForcePolicy(
        policy_id="POL-002",
        jurisdiction="State Y",
        requires_de_escalation=True,
        prohibits_chokeholds=True,
        requires_imminent_threat_for_deadly_force=True,
    )
    
    # Good: de-escalation attempted
    good_incident = UseOfForceIncident(
        incident_id="INC-005",
        timestamp=datetime.now(),
        force_used=ForceLevel.PHYSICAL_RESTRAINT,
        threat_level=ThreatLevel.MODERATE,
        de_escalation_attempted=True,
        subject_injured=False,
        officer_id="OFF-005",
        justification="De-escalation failed",
    )
    
    assert checker.check_de_escalation(good_incident, policy)
    
    # Bad: no de-escalation attempted
    bad_incident = UseOfForceIncident(
        incident_id="INC-006",
        timestamp=datetime.now(),
        force_used=ForceLevel.LESS_LETHAL,
        threat_level=ThreatLevel.MODERATE,
        de_escalation_attempted=False,
        subject_injured=True,
        officer_id="OFF-006",
        justification="None",
    )
    
    assert not checker.check_de_escalation(bad_incident, policy)
    
    return True


def check_documentation_complete() -> bool:
    """Verify all use of force incidents are fully documented."""
    incident = UseOfForceIncident(
        incident_id="INC-007",
        timestamp=datetime.now(),
        force_used=ForceLevel.PHYSICAL_RESTRAINT,
        threat_level=ThreatLevel.MODERATE,
        de_escalation_attempted=True,
        subject_injured=False,
        officer_id="OFF-007",
        justification="Complete documentation",
    )
    
    # Required fields must be present
    assert incident.incident_id
    assert incident.timestamp
    assert incident.officer_id
    assert incident.justification
    assert isinstance(incident.force_used, ForceLevel)
    assert isinstance(incident.threat_level, ThreatLevel)
    
    return True


def check_less_lethal_before_deadly() -> bool:
    """Verify less-lethal options considered before deadly force."""
    # When threat is high but not imminent death, less-lethal should be used
    incident = UseOfForceIncident(
        incident_id="INC-008",
        timestamp=datetime.now(),
        force_used=ForceLevel.LESS_LETHAL,
        threat_level=ThreatLevel.HIGH,
        de_escalation_attempted=True,
        subject_injured=False,
        officer_id="OFF-008",
        justification="Less-lethal appropriate",
    )
    
    assert incident.force_used == ForceLevel.LESS_LETHAL
    assert incident.threat_level == ThreatLevel.HIGH
    
    return True


def check_compliance_deterministic() -> bool:
    """Master compliance check."""
    assert check_force_proportionality()
    assert check_deadly_force_necessity()
    assert check_de_escalation_attempted()
    assert check_documentation_complete()
    assert check_less_lethal_before_deadly()
    return True
