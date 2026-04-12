"""D_USE_OF_FORCE invariants — Yeshua Standard. 0 floats.

Standards:
- Tennessee v. Garner, 471 U.S. 1 (1985) — deadly force only for fleeing felon with imminent threat
- Graham v. Connor, 490 U.S. 386 (1989) — objective reasonableness standard
- President's Task Force on 21st Century Policing (2015) — de-escalation
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import UseOfForceIncident, ForcePolicy, ForceLevel, ThreatLevel


def check_force_proportionality(incident: UseOfForceIncident) -> Tuple[bool, ProofObject]:
    """Verify force level is proportional to threat level.

    Standard: Graham v. Connor, 490 U.S. 386 (1989)
    falsifies_if: force_used is DEADLY_FORCE and threat_level is not IMMINENT_DEATH.
    """
    # Deadly force only permissible for imminent death threat
    if incident.force_used == ForceLevel.DEADLY_FORCE:
        ok = incident.threat_level == ThreatLevel.IMMINENT_DEATH
    elif incident.force_used == ForceLevel.LESS_LETHAL:
        ok = incident.threat_level in (ThreatLevel.HIGH, ThreatLevel.IMMINENT_DEATH)
    elif incident.force_used == ForceLevel.PHYSICAL_RESTRAINT:
        ok = incident.threat_level in (ThreatLevel.MODERATE, ThreatLevel.HIGH, ThreatLevel.IMMINENT_DEATH)
    else:  # VERBAL
        ok = True
    premises = [
        f"incident_id={incident.incident_id}",
        f"force_used={incident.force_used.value}",
        f"threat_level={incident.threat_level.value}",
    ]
    return ok, ProofObject(
        rule="ForceProportionality",
        premises=premises,
        conclusion="PASS: force proportional to threat" if ok else "VIOLATION: force disproportionate to threat",
    )


def check_deadly_force_necessity(incident: UseOfForceIncident, policy: ForcePolicy) -> Tuple[bool, ProofObject]:
    """Deadly force only when imminent threat of death/serious bodily injury.

    Standard: Tennessee v. Garner, 471 U.S. 1 (1985)
    falsifies_if: force_used is DEADLY_FORCE and policy.requires_imminent_threat_for_deadly_force is True
                  but threat_level is not IMMINENT_DEATH.
    """
    if incident.force_used == ForceLevel.DEADLY_FORCE and policy.requires_imminent_threat_for_deadly_force:
        ok = incident.threat_level == ThreatLevel.IMMINENT_DEATH
    else:
        ok = True
    premises = [
        f"incident_id={incident.incident_id}",
        f"deadly_force={incident.force_used == ForceLevel.DEADLY_FORCE}",
        f"policy_requires_imminent={policy.requires_imminent_threat_for_deadly_force}",
        f"threat_level={incident.threat_level.value}",
    ]
    return ok, ProofObject(
        rule="DeadlyForceNecessity",
        premises=premises,
        conclusion="PASS: deadly force necessity satisfied" if ok else "VIOLATION: deadly force without imminent threat",
    )


def check_de_escalation_attempted(incident: UseOfForceIncident, policy: ForcePolicy) -> Tuple[bool, ProofObject]:
    """De-escalation must be attempted before physical force when policy requires it.

    Standard: COPS Office De-Escalation Policy Framework (2019)
    falsifies_if: policy.requires_de_escalation is True and force_used > VERBAL
                  but de_escalation_attempted is False.
    """
    if policy.requires_de_escalation and incident.force_used != ForceLevel.VERBAL:
        ok = incident.de_escalation_attempted
    else:
        ok = True
    premises = [
        f"incident_id={incident.incident_id}",
        f"requires_de_escalation={policy.requires_de_escalation}",
        f"force_used={incident.force_used.value}",
        f"de_escalation_attempted={incident.de_escalation_attempted}",
    ]
    return ok, ProofObject(
        rule="DeEscalationAttempted",
        premises=premises,
        conclusion="PASS: de-escalation requirement satisfied" if ok else "VIOLATION: de-escalation not attempted",
    )


def check_chokehold_prohibition(incident: UseOfForceIncident, policy: ForcePolicy) -> Tuple[bool, ProofObject]:
    """Chokeholds prohibited where policy bans them.

    Standard: George Floyd Justice in Policing Act proposals; NYC, CA, CO statutes
    falsifies_if: policy.prohibits_chokeholds is True and chokehold technique was used
                  (inferred from PHYSICAL_RESTRAINT + subject_injured).
    """
    # Proxy: physical restraint that injures subject in a chokehold-prohibiting jurisdiction
    chokehold_likely = (
        incident.force_used == ForceLevel.PHYSICAL_RESTRAINT
        and incident.subject_injured
        and "chokehold" in incident.justification.lower()
    )
    ok = not (policy.prohibits_chokeholds and chokehold_likely)
    premises = [
        f"incident_id={incident.incident_id}",
        f"prohibits_chokeholds={policy.prohibits_chokeholds}",
        f"force_used={incident.force_used.value}",
        f"subject_injured={incident.subject_injured}",
        f"chokehold_likely={chokehold_likely}",
    ]
    return ok, ProofObject(
        rule="ChokeholdProhibition",
        premises=premises,
        conclusion="PASS: chokehold policy satisfied" if ok else "VIOLATION: chokehold used in prohibited jurisdiction",
    )


def check_incident_documentation(incident: UseOfForceIncident) -> Tuple[bool, ProofObject]:
    """All use of force incidents must have a non-empty justification.

    Standard: DOJ Consent Decree reporting requirements; 42 U.S.C. §3789d
    falsifies_if: justification is empty string.
    """
    ok = len(incident.justification.strip()) > 0
    premises = [
        f"incident_id={incident.incident_id}",
        f"officer_id={incident.officer_id}",
        f"justification_length={len(incident.justification.strip())}",
    ]
    return ok, ProofObject(
        rule="IncidentDocumentation",
        premises=premises,
        conclusion="PASS: incident documented" if ok else "VIOLATION: missing use-of-force justification",
    )


def check_threat_assessment_ratio(incident: UseOfForceIncident) -> Tuple[bool, ProofObject]:
    """Force level ordinal must not exceed threat level ordinal + 1.

    Standard: Graham v. Connor objective reasonableness
    falsifies_if: force_ordinal > threat_ordinal + 1.
    """
    force_ord = {
        ForceLevel.VERBAL: Fraction(0),
        ForceLevel.PHYSICAL_RESTRAINT: Fraction(1),
        ForceLevel.LESS_LETHAL: Fraction(2),
        ForceLevel.DEADLY_FORCE: Fraction(3),
    }
    threat_ord = {
        ThreatLevel.NONE: Fraction(0),
        ThreatLevel.LOW: Fraction(1),
        ThreatLevel.MODERATE: Fraction(2),
        ThreatLevel.HIGH: Fraction(3),
        ThreatLevel.IMMINENT_DEATH: Fraction(4),
    }
    f = force_ord[incident.force_used]
    t = threat_ord[incident.threat_level]
    ok = f <= t + Fraction(1)
    premises = [
        f"incident_id={incident.incident_id}",
        f"force_ordinal={f}",
        f"threat_ordinal={t}",
        f"allowed_max={t + Fraction(1)}",
    ]
    return ok, ProofObject(
        rule="ThreatAssessmentRatio",
        premises=premises,
        conclusion="PASS: force within one level of threat" if ok else f"VIOLATION: force ordinal {f} > threat + 1 = {t+1}",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    from datetime import datetime
    incident = UseOfForceIncident(
        incident_id="TEST-001",
        timestamp=datetime.now(),
        force_used=ForceLevel.VERBAL,
        threat_level=ThreatLevel.LOW,
        de_escalation_attempted=True,
        subject_injured=False,
        officer_id="OFF-001",
        justification="Subject non-compliant with verbal commands",
    )
    policy = ForcePolicy(
        policy_id="POL-001",
        jurisdiction="Test City",
        requires_de_escalation=True,
        prohibits_chokeholds=True,
        requires_imminent_threat_for_deadly_force=True,
    )
    results = {}
    ok1, p1 = check_force_proportionality(incident)
    results["check_force_proportionality"] = p1.conclusion
    ok2, p2 = check_deadly_force_necessity(incident, policy)
    results["check_deadly_force_necessity"] = p2.conclusion
    ok3, p3 = check_de_escalation_attempted(incident, policy)
    results["check_de_escalation_attempted"] = p3.conclusion
    ok4, p4 = check_chokehold_prohibition(incident, policy)
    results["check_chokehold_prohibition"] = p4.conclusion
    ok5, p5 = check_incident_documentation(incident)
    results["check_incident_documentation"] = p5.conclusion
    ok6, p6 = check_threat_assessment_ratio(incident)
    results["check_threat_assessment_ratio"] = p6.conclusion
    return results
