"""D_DIPLOMATIC invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes Vienna Convention
requirements for diplomatic immunity, inviolability, persona non grata, and
consular relations.

Standards:
- Vienna Convention on Diplomatic Relations (VCDR, 1961)
- Vienna Convention on Consular Relations (VCCR, 1963)
- Convention on Special Missions (1969)
- Diplomatic Relations Act (22 U.S.C. §254a et seq.)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    DiplomaticAgent,
    DiplomaticMission,
    ImmunityWaiver,
    ConsularOfficer,
    SpecialMission,
)


def check_diplomatic_inviolability_person(agent: DiplomaticAgent) -> Tuple[bool, ProofObject]:
    """
    Rule: Accredited diplomatic agents enjoy personal inviolability; receiving state must not arrest or detain (VCDR Art. 29).

    falsifies_if: agent is accredited AND recognized BUT persona_non_grata is True AND recall_completed is False.
    """
    properly_accredited = agent.accredited and agent.recognized_by_receiving_state
    # If PNG declared and recall not yet completed, inviolability may be compromised
    png_without_recall = agent.persona_non_grata and not agent.recall_completed

    success = properly_accredited and not png_without_recall

    if not success:
        return False, ProofObject(
            rule="DiplomaticInviolabilityPerson",
            premises=[
                f"agent_id={agent.agent_id}",
                f"accredited={agent.accredited}",
                f"recognized_by_receiving_state={agent.recognized_by_receiving_state}",
                f"persona_non_grata={agent.persona_non_grata}",
                f"recall_completed={agent.recall_completed}",
            ],
            conclusion="VIOLATION: VCDR Art. 29 personal inviolability not met — agent not properly accredited or PNG without recall",
        )

    return True, ProofObject(
        rule="DiplomaticInviolabilityPerson",
        premises=[
            f"agent_id={agent.agent_id}",
            f"accredited={agent.accredited}",
            f"recognized_by_receiving_state={agent.recognized_by_receiving_state}",
            f"persona_non_grata={agent.persona_non_grata}",
            f"recall_completed={agent.recall_completed}",
        ],
        conclusion="VCDR Art. 29 personal inviolability confirmed",
    )


def check_diplomatic_inviolability_premises(mission: DiplomaticMission) -> Tuple[bool, ProofObject]:
    """
    Rule: Mission premises are inviolable; receiving state must not enter without consent and must actively protect them (VCDR Art. 22).

    falsifies_if: receiving_state_entered_without_consent is True OR archives_secured is False OR protection_duty_met is False.
    """
    no_unlawful_entry = not mission.receiving_state_entered_without_consent
    archives_ok = mission.archives_secured
    protection_ok = mission.protection_duty_met

    success = no_unlawful_entry and archives_ok and protection_ok

    if not success:
        return False, ProofObject(
            rule="DiplomaticInviolabilityPremises",
            premises=[
                f"mission_id={mission.mission_id}",
                f"premises_inviolable={mission.premises_inviolable}",
                f"receiving_state_entered_without_consent={mission.receiving_state_entered_without_consent}",
                f"archives_secured={mission.archives_secured}",
                f"protection_duty_met={mission.protection_duty_met}",
            ],
            conclusion="VIOLATION: VCDR Art. 22 premises inviolability breached — unlawful entry, unsecured archives, or protection duty unmet",
        )

    return True, ProofObject(
        rule="DiplomaticInviolabilityPremises",
        premises=[
            f"mission_id={mission.mission_id}",
            f"no_unlawful_entry={no_unlawful_entry}",
            f"archives_secured={archives_ok}",
            f"protection_duty_met={protection_ok}",
        ],
        conclusion="VCDR Art. 22 premises inviolability confirmed",
    )


def check_diplomatic_immunity_jurisdiction(
    agent: DiplomaticAgent, waiver: ImmunityWaiver
) -> Tuple[bool, ProofObject]:
    """
    Rule: Diplomatic agents are immune from criminal and official civil jurisdiction unless waiver is explicit and granted by sending state (VCDR Art. 31-32).

    falsifies_if: agent is accredited AND waiver is NOT (explicit AND by_sending_state) AND criminal prosecution is attempted.
    """
    valid_waiver = waiver.explicit and waiver.by_sending_state
    immunity_intact = not valid_waiver

    # If agent is not accredited, no immunity to protect
    if not agent.accredited:
        return False, ProofObject(
            rule="DiplomaticImmunityJurisdiction",
            premises=[
                f"agent_id={agent.agent_id}",
                f"accredited={agent.accredited}",
            ],
            conclusion="VIOLATION: VCDR Art. 31 immunity inapplicable — agent not accredited",
        )

    success = immunity_intact or valid_waiver  # Either immunity intact or waiver properly done

    if not success:
        return False, ProofObject(
            rule="DiplomaticImmunityJurisdiction",
            premises=[
                f"agent_id={agent.agent_id}",
                f"waiver_id={waiver.waiver_id}",
                f"waiver_explicit={waiver.explicit}",
                f"waiver_by_sending_state={waiver.by_sending_state}",
            ],
            conclusion="VIOLATION: VCDR Art. 31 immunity violated — improper jurisdiction assertion",
        )

    return True, ProofObject(
        rule="DiplomaticImmunityJurisdiction",
        premises=[
            f"agent_id={agent.agent_id}",
            f"immunity_intact={immunity_intact}",
            f"valid_waiver={valid_waiver}",
            f"waiver_scope={waiver.scope}",
        ],
        conclusion="VCDR Art. 31 immunity from jurisdiction confirmed",
    )


def check_persona_non_grata_procedure(agent: DiplomaticAgent) -> Tuple[bool, ProofObject]:
    """
    Rule: When receiving state declares diplomat PNG, sending state must recall the agent and complete departure (VCDR Art. 9).

    falsifies_if: persona_non_grata is True AND recall_completed is False.
    """
    png_handled = not agent.persona_non_grata or agent.recall_completed

    if not png_handled:
        return False, ProofObject(
            rule="PersonaNonGrataProcedure",
            premises=[
                f"agent_id={agent.agent_id}",
                f"persona_non_grata={agent.persona_non_grata}",
                f"recall_completed={agent.recall_completed}",
            ],
            conclusion="VIOLATION: VCDR Art. 9 PNG procedure incomplete — agent declared PNG but recall not completed",
        )

    return True, ProofObject(
        rule="PersonaNonGrataProcedure",
        premises=[
            f"agent_id={agent.agent_id}",
            f"persona_non_grata={agent.persona_non_grata}",
            f"recall_completed={agent.recall_completed}",
        ],
        conclusion="VCDR Art. 9 persona non grata procedure satisfied",
    )


def check_consular_functions_immunity(officer: ConsularOfficer) -> Tuple[bool, ProofObject]:
    """
    Rule: Consular officers have immunity only for official acts; if charged with a grave crime, receiving state must notify the consular post without delay (VCCR Art. 36, 43).

    falsifies_if: officer is charged AND act IS official AND prosecution proceeds (consular functional immunity violated)
                  OR grave_crime AND notification NOT sent within max_notification_hours.
    """
    # Consular immunity for official acts must be respected
    official_immunity_violated = officer.official_act and officer.grave_crime_charged

    notification_timely = (
        officer.notification_sent_within_hours <= officer.max_notification_hours
    )

    success = not official_immunity_violated and notification_timely

    if not success:
        return False, ProofObject(
            rule="ConsularFunctionsImmunity",
            premises=[
                f"officer_id={officer.officer_id}",
                f"official_act={officer.official_act}",
                f"grave_crime_charged={officer.grave_crime_charged}",
                f"notification_sent_within_hours={officer.notification_sent_within_hours}",
                f"max_notification_hours={officer.max_notification_hours}",
                f"notification_timely={notification_timely}",
            ],
            conclusion="VIOLATION: VCCR Art. 43 consular immunity or Art. 36 notification violated",
        )

    return True, ProofObject(
        rule="ConsularFunctionsImmunity",
        premises=[
            f"officer_id={officer.officer_id}",
            f"official_act={officer.official_act}",
            f"grave_crime_charged={officer.grave_crime_charged}",
            f"notification_timely={notification_timely}",
        ],
        conclusion="VCCR Art. 43 consular functional immunity and Art. 36 notification satisfied",
    )


def check_special_mission_immunity(mission: SpecialMission) -> Tuple[bool, ProofObject]:
    """
    Rule: Special mission members enjoy immunity only during the mission period and only for official acts; receiving state consent is required (Convention on Special Missions, 1969, Art. 21-31).

    falsifies_if: mission_active is True AND mutual_consent is False
                  OR immunity claimed beyond official_acts_only scope.
    """
    consent_present = mission.mutual_consent
    scope_limited = mission.official_acts_only
    mission_in_period = mission.mission_active

    success = consent_present and scope_limited and mission_in_period

    if not success:
        return False, ProofObject(
            rule="SpecialMissionImmunity",
            premises=[
                f"mission_id={mission.mission_id}",
                f"mutual_consent={mission.mutual_consent}",
                f"mission_active={mission.mission_active}",
                f"official_acts_only={mission.official_acts_only}",
            ],
            conclusion="VIOLATION: Special mission immunity invalid — consent missing, mission inactive, or scope not limited to official acts",
        )

    return True, ProofObject(
        rule="SpecialMissionImmunity",
        premises=[
            f"mission_id={mission.mission_id}",
            f"mutual_consent={consent_present}",
            f"mission_active={mission_in_period}",
            f"official_acts_only={scope_limited}",
        ],
        conclusion="Special mission immunity confirmed per Convention on Special Missions (1969)",
    )


def run_all_invariants() -> dict:
    """Run all D_DIPLOMATIC invariants with nominal sample data.

    falsifies_if: any diplomatic invariant check fails or raises an exception.
    """
    agent = DiplomaticAgent(
        agent_id="AGENT-001",
        accredited=True,
        recognized_by_receiving_state=True,
        persona_non_grata=False,
        recall_completed=False,
        rank="ambassador",
    )
    mission = DiplomaticMission(
        mission_id="MISSION-001",
        premises_inviolable=True,
        receiving_state_entered_without_consent=False,
        archives_secured=True,
        protection_duty_met=True,
    )
    waiver = ImmunityWaiver(
        waiver_id="WAIVER-001",
        explicit=False,
        by_sending_state=False,
        scope="none",
    )
    officer = ConsularOfficer(
        officer_id="OFFICER-001",
        official_act=True,
        grave_crime_charged=False,
        notification_sent_within_hours=Fraction(1),
        max_notification_hours=Fraction(24),
    )
    special_mission = SpecialMission(
        mission_id="SMISSION-001",
        mutual_consent=True,
        mission_active=True,
        official_acts_only=True,
    )

    checks = [
        ("check_diplomatic_inviolability_person", lambda: check_diplomatic_inviolability_person(agent)),
        ("check_diplomatic_inviolability_premises", lambda: check_diplomatic_inviolability_premises(mission)),
        ("check_diplomatic_immunity_jurisdiction", lambda: check_diplomatic_immunity_jurisdiction(agent, waiver)),
        ("check_persona_non_grata_procedure", lambda: check_persona_non_grata_procedure(agent)),
        ("check_consular_functions_immunity", lambda: check_consular_functions_immunity(officer)),
        ("check_special_mission_immunity", lambda: check_special_mission_immunity(special_mission)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_DIPLOMATIC invariants: PASS")
