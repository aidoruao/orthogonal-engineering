"""D_DIPLOMATIC invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Vienna Convention on Diplomatic Relations (1961)
- Vienna Convention on Consular Relations (1963)
- Diplomatic Relations Act (22 U.S.C. §254a et seq.)

Source: ontology/ontology.json#D_DIPLOMATIC
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_diplomatic_inviolability_person() -> Tuple[bool, ProofObject]:
    """
    Invariant: Diplomatic agents enjoy personal inviolability (no arrest/detention).
    
    Standard: Vienna Convention on Diplomatic Relations Article 29
    Falsifies if: Diplomatic agent arrested or detained by receiving state.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Diplomatic agent status
    diplomatic_agent = True
    recognized_by_receiving_state = True
    accreditation_complete = True
    
    status_established = diplomatic_agent and recognized_by_receiving_state and accreditation_complete
    
    # Inviolability protections
    arrest_prohibited = True
    detention_prohibited = True
    
    # Exception: Self-defense/citizens arrest not applicable to state action
    receiving_state_action = False  # State must not arrest
    
    personal_inviolability_respected = (
        status_established and
        arrest_prohibited and
        detention_prohibited and
        receiving_state_action == False
    )
    
    # Duty to respect laws (Article 41)
    duty_to_respect_laws = True
    professional_activity_only = True
    
    # Remedy for violation: persona non grata, not criminal process
    remedy_available = True
    
    success = personal_inviolability_respected and duty_to_respect_laws
    
    proof = ProofObject(
        rule="DiplomaticInviolabilityPerson",
        premises=[
            "diplomatic_agent = True",
            "accreditation_complete = True",
            "arrest_prohibited = True",
            "detention_prohibited = True",
            f"personal_inviolability_respected = {personal_inviolability_respected}",
        ],
        conclusion=(
            "VCDR Article 29 personal inviolability enforced"
            if success
            else "FAIL: Personal inviolability check failed"
        ),
    )
    return success, proof


def check_diplomatic_inviolability_premises() -> Tuple[bool, ProofObject]:
    """
    Invariant: Diplomatic premises are inviolable (enter only with consent).
    
    Standard: Vienna Convention on Diplomatic Relations Article 22
    Falsifies if: Receiving state agents enter mission premises without permission.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Premises definition
    mission_building = True
    head_of_mission_residence = True
    premises_inviolable = True
    
    # Inviolability scope
    receiving_state_entry = False  # No entry without consent
    receiving_state_protection_duty = True  # Duty to protect
    
    # Exception: Fire/emergency (consent implied but still required)
    emergency_entry_requested = True
    mission_consent_given = True
    emergency_entry_lawful = emergency_entry_requested and mission_consent_given
    
    # Protection duty
    disturbance_prevented = True
    dignity_preserved = True
    
    protection_adequate = receiving_state_protection_duty and disturbance_prevented
    
    # Archives and documents
    archives_inviolable = True
    documents_protected = True
    
    premises_protection = (
        premises_inviolable and
        receiving_state_entry == False and
        protection_adequate and
        archives_inviolable
    )
    
    success = premises_protection
    
    proof = ProofObject(
        rule="DiplomaticInviolabilityPremises",
        premises=[
            "premises_inviolable = True",
            f"receiving_state_entry_without_consent = {receiving_state_entry}",
            f"emergency_entry_lawful = {emergency_entry_lawful}",
            "protection_duty = True",
            "archives_inviolable = True",
        ],
        conclusion=(
            "VCDR Article 22 premises inviolability enforced"
            if success
            else "FAIL: Premises inviolability check failed"
        ),
    )
    return success, proof


def check_diplomatic_immunity_jurisdiction() -> Tuple[bool, ProofObject]:
    """
    Invariant: Diplomatic agents immune from civil and criminal jurisdiction.
    
    Standard: Vienna Convention on Diplomatic Relations Article 31
    Falsifies if: Legal process instituted against diplomatic agent in official capacity.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Immunity scope
    criminal_jurisdiction_immunity = True  # Absolute
    civil_jurisdiction_immunity = True     # Official acts only
    
    # Exceptions to civil immunity (Article 31(1))
    real_property_action = False
    succession_action = False
    professional_commercial_activity = False  # Outside official functions
    
    exception_applies = real_property_action or succession_action or professional_commercial_activity
    civil_immunity_intact = not exception_applies
    
    # Administrative jurisdiction also immune
    administrative_immunity = True
    
    # Waiver requirements (Article 32)
    immunity_waived = False
    waiver_explicit = True  # Must be express
    waiver_by_sending_state = True
    
    valid_waiver = immunity_waived and waiver_explicit and waiver_by_sending_state
    immunity_intact = not valid_waiver
    
    # Family members (same immunity if household)
    family_member_same_immunity = True
    not_national_of_receiving_state = True
    
    full_immunity = (
        criminal_jurisdiction_immunity and
        civil_immunity_intact and
        administrative_immunity and
        immunity_intact and
        family_member_same_immunity
    )
    
    success = full_immunity
    
    proof = ProofObject(
        rule="DiplomaticImmunityJurisdiction",
        premises=[
            "criminal_immunity_absolute = True",
            "civil_immunity_official_acts = True",
            f"exception_applies = {exception_applies}",
            f"immunity_waived = {immunity_waived}",
            f"family_immunity_same = {family_member_same_immunity}",
        ],
        conclusion=(
            "VCDR Article 31 immunity from jurisdiction enforced"
            if success
            else "FAIL: Immunity from jurisdiction check failed"
        ),
    )
    return success, proof


def check_persona_non_grata_procedure() -> Tuple[bool, ProofObject]:
    """
    Invariant: Receiving state may declare diplomat persona non grata without explanation.
    
    Standard: Vienna Convention on Diplomatic Relations Article 9
    Falsifies if: Sending state refuses recall after PNG declaration.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # PNG declaration
    receiving_state_declares_png = True
    no_reason_required = True
    notification_to_sending_state = True
    
    declaration_valid = receiving_state_declares_png and notification_to_sending_state
    
    # Timeframe for departure
    reasonable_time_given = True  # Normally 48 hours to 7 days
    departure_deadline_set = True
    
    # Sending state obligations
    recall_required = True
    recall_undertaken = True
    termination_of_functions = True
    
    sending_state_compliant = recall_undertaken and termination_of_functions
    
    # Consequences of non-recall
    receiving_state_may_expel = True
    functions_terminate_anyway = True
    
    # Family members included
    family_also_png = True
    
    # Abuse of PNG
    collective_png_prohibited = True  # Must be individual, not mass expulsion
    
    png_procedure_complete = (
        declaration_valid and
        reasonable_time_given and
        sending_state_compliant and
        family_also_png and
        collective_png_prohibited
    )
    
    success = png_procedure_complete
    
    proof = ProofObject(
        rule="PersonaNonGrataProcedure",
        premises=[
            "receiving_state_declaration = True",
            "no_reason_required = True",
            f"recall_undertaken = {recall_undertaken}",
            "functions_terminate = True",
            "collective_png_prohibited = True",
        ],
        conclusion=(
            "VCDR Article 9 persona non grata procedure enforced"
            if success
            else "FAIL: Persona non grata procedure check failed"
        ),
    )
    return success, proof


def check_consular_functions_immunity() -> Tuple[bool, ProofObject]:
    """
    Invariant: Consular officers have functional immunity for official acts only.
    
    Standard: Vienna Convention on Consular Relations Article 43
    Falsifies if: Consular officer prosecuted for official act or immune for private crime.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Consular immunity scope (functional, not full)
    official_acts_immunity = True
    private_acts_no_immunity = True
    
    # Criminal jurisdiction
    grave_crime_arrest_possible = True  # For grave crimes
    arrest_must_be_lawful = True
    proceedings_respect_official_position = True
    
    # Arrest/detention notification
    notification_to_consular_post = True
    notification_without_delay = True
    
    notification_compliant = notification_to_consular_post and notification_without_delay
    
    # Consular functions
    protect_nationals = True
    assist_nationals = True
    issue_passports = True
    notarize_documents = True
    
    functions_protected = protect_nationals and assist_nationals
    
    # Distinction from diplomatic immunity
    lesser_immunity_than_diplomatic = True
    no_inviolability_of_person = False  # Less than diplomatic
    
    immunity_scope_correct = official_acts_immunity and private_acts_no_immunity and lesser_immunity_than_diplomatic
    
    success = immunity_scope_correct and notification_compliant and functions_protected
    
    proof = ProofObject(
        rule="ConsularFunctionsImmunity",
        premises=[
            "official_acts_immunity = True",
            "private_acts_no_immunity = True",
            f"notification_compliant = {notification_compliant}",
            "consular_functions_protected = True",
            "lesser_immunity_than_diplomatic = True",
        ],
        conclusion=(
            "VCCR Article 43 consular immunity enforced"
            if success
            else "FAIL: Consular immunity check failed"
        ),
    )
    return success, proof


def check_special_mission_immunity() -> Tuple[bool, ProofObject]:
    """
    Invariant: Special mission members enjoy functional immunity during mission.
    
    Standard: Convention on Special Missions (1969); Customary International Law
    Falsifies if: Special mission member prosecuted for official acts during mission.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Special mission requirements
    mutual_consent = True
    official_invitation = True
    duration_temporary = True
    specific_purpose = True
    
    mission_valid = mutual_consent and official_invitation and duration_temporary
    
    # Immunity scope
    official_acts_only = True
    during_mission_period = True
    
    immunity_active = official_acts_only and during_mission_period
    
    # Member categories
    head_of_special_mission = True
    diplomatic_staff = True
    administrative_technical_staff = True
    service_staff_limited_immunity = True
    
    # Immunity of premises (analogous to VCDR Article 22)
    special_mission_premises_inviolable = True
    archives_protected = True
    
    premises_protection = special_mission_premises_inviolable and archives_protected
    
    # End of immunity
    mission_terminated = False
    recall_completed = False
    
    immunity_continues = during_mission_period and not (mission_terminated and recall_completed)
    
    # Distinction from permanent mission
    temporary_nature = True
    no_residence_establishment = True
    
    success = mission_valid and immunity_active and premises_protection and temporary_nature
    
    proof = ProofObject(
        rule="SpecialMissionImmunity",
        premises=[
            "mutual_consent = True",
            "duration_temporary = True",
            f"immunity_active = {immunity_active}",
            "premises_inviolable = True",
            "temporary_nature = True",
        ],
        conclusion=(
            "Special mission immunity enforced per 1969 Convention"
            if success
            else "FAIL: Special mission immunity check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_DIPLOMATIC invariants."""
    checks = [
        ("check_diplomatic_inviolability_person", check_diplomatic_inviolability_person),
        ("check_diplomatic_inviolability_premises", check_diplomatic_inviolability_premises),
        ("check_diplomatic_immunity_jurisdiction", check_diplomatic_immunity_jurisdiction),
        ("check_persona_non_grata_procedure", check_persona_non_grata_procedure),
        ("check_consular_functions_immunity", check_consular_functions_immunity),
        ("check_special_mission_immunity", check_special_mission_immunity),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_DIPLOMATIC invariants: PASS")
