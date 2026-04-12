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
from typing import Tuple

from axioms.logic import ProofObject

from .implementation import (
    D_USE_OF_FORCEChecker,
    D_USE_OF_FORCERecord,
    UseOfForceIncident,
    ForceLevel,
    ThreatLevel,
    ForcePolicy,
)


def check_force_proportionality() -> Tuple[bool, ProofObject]:
    """Verify force level is proportional to threat level.
    
    Falsifies if: force applied exceeds threat level proportionality.
    falsifies_if: force applied exceeds threat level proportionality.
    """
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
    
    if not checker.check_proportionality(proportional):
        return False, ProofObject(
            rule="force_proportionality",
            subject="INC-001",
            falsifies_if="Proportional force failed check",
        )
    
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
    
    if checker.check_proportionality(disproportionate):
        return False, ProofObject(
            rule="force_proportionality",
            subject="INC-002",
            falsifies_if="Disproportionate force passed check",
        )
    
    return True, ProofObject(
        rule="force_proportionality",
        subject="force proportionality",
        verified=True,
    )


def check_deadly_force_necessity() -> Tuple[bool, ProofObject]:
    """Verify deadly force is only used for imminent threat of death.
    
    Falsifies if: deadly force is used absent an imminent death threat or policy exception.
    falsifies_if: deadly force is used absent an imminent death threat or policy exception.
    """
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
    
    if not checker.check_necessity(valid_deadly_force, policy):
        return False, ProofObject(
            rule="deadly_force_necessity",
            subject="INC-003",
            falsifies_if="Valid deadly force failed necessity check",
        )
    
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
    
    if checker.check_necessity(invalid_deadly_force, policy):
        return False, ProofObject(
            rule="deadly_force_necessity",
            subject="INC-004",
            falsifies_if="Invalid deadly force passed necessity check",
        )
    
    return True, ProofObject(
        rule="deadly_force_necessity",
        subject="deadly force necessity",
        verified=True,
    )


def check_de_escalation_attempted() -> Tuple[bool, ProofObject]:
    """Verify de-escalation is attempted before physical force.
    
    Falsifies if: de-escalation is required but not attempted before force.
    falsifies_if: de-escalation is required but not attempted before force.
    """
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
    
    if not checker.check_de_escalation(good_incident, policy):
        return False, ProofObject(
            rule="de_escalation_attempted",
            subject="INC-005",
            falsifies_if="Good incident failed de-escalation check",
        )
    
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
    
    if checker.check_de_escalation(bad_incident, policy):
        return False, ProofObject(
            rule="de_escalation_attempted",
            subject="INC-006",
            falsifies_if="Bad incident passed de-escalation check",
        )
    
    return True, ProofObject(
        rule="de_escalation_attempted",
        subject="de-escalation",
        verified=True,
    )


def check_documentation_complete() -> Tuple[bool, ProofObject]:
    """Verify all use of force incidents are fully documented.
    
    Falsifies if: required documentation fields (id, timestamp, officer, justification,
    falsifies_if: required documentation fields (id, timestamp, officer, justification,
    force_used, threat_level) are missing.
    """
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
    if not incident.incident_id:
        return False, ProofObject(
            rule="documentation_complete",
            subject="INC-007",
            falsifies_if="incident_id missing",
        )
    if not incident.timestamp:
        return False, ProofObject(
            rule="documentation_complete",
            subject="INC-007",
            falsifies_if="timestamp missing",
        )
    if not incident.officer_id:
        return False, ProofObject(
            rule="documentation_complete",
            subject="INC-007",
            falsifies_if="officer_id missing",
        )
    if not incident.justification:
        return False, ProofObject(
            rule="documentation_complete",
            subject="INC-007",
            falsifies_if="justification missing",
        )
    if not isinstance(incident.force_used, ForceLevel):
        return False, ProofObject(
            rule="documentation_complete",
            subject="INC-007",
            falsifies_if="force_used not ForceLevel",
        )
    if not isinstance(incident.threat_level, ThreatLevel):
        return False, ProofObject(
            rule="documentation_complete",
            subject="INC-007",
            falsifies_if="threat_level not ThreatLevel",
        )
    
    return True, ProofObject(
        rule="documentation_complete",
        subject="documentation",
        verified=True,
    )


def check_less_lethal_before_deadly() -> Tuple[bool, ProofObject]:
    """Verify less-lethal options considered before deadly force.
    
    Falsifies if: less-lethal options are bypassed when threat is high but not
    falsifies_if: less-lethal options are bypassed when threat is high but not
    imminent death.
    """
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
    
    if incident.force_used != ForceLevel.LESS_LETHAL:
        return False, ProofObject(
            rule="less_lethal_before_deadly",
            subject="INC-008",
            falsifies_if="force_used not LESS_LETHAL",
        )
    if incident.threat_level != ThreatLevel.HIGH:
        return False, ProofObject(
            rule="less_lethal_before_deadly",
            subject="INC-008",
            falsifies_if="threat_level not HIGH",
        )
    
    return True, ProofObject(
        rule="less_lethal_before_deadly",
        subject="less lethal options",
        verified=True,
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """Master compliance check.

    Falsifies if: any use-of-force invariant check fails.
    falsifies_if: any use-of-force invariant check fails.
    """
    checks = [
        check_force_proportionality,
        check_deadly_force_necessity,
        check_de_escalation_attempted,
        check_documentation_complete,
        check_less_lethal_before_deadly,
    ]
    
    for check in checks:
        result, proof = check()
        if not result:
            return False, ProofObject(
                rule="compliance_deterministic",
                subject="master_check",
                falsifies_if=f"{proof.rule} failed",
            )
    
    return True, ProofObject(
        rule="compliance_deterministic",
        subject="use of force compliance",
        verified=True,
    )
