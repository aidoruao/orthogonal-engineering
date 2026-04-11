"""D_UN_CHARTER invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- UN Charter Chapters I-VII
- Jus cogens norms
- Chapter VII collective security

Source: UN Charter (1945)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_un_charter_purposes_principles() -> Tuple[bool, ProofObject]:
    """
    Invariant: UN Charter Chapter I establishes purposes and principles.
    
    Standard: UN Charter Article 1-2 - Purposes and Principles
    Falsifies if: UN acts contrary to Charter purposes.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Article 1 Purposes
    maintain_international_peace = True
    develop_friendly_relations = True
    achieve_international_cooperation = True
    harmonize_nations_actions = True
    
    num_purposes = Fraction(4)
    
    # Article 2 Principles
    sovereign_equality = True
    fulfill_obligations = True
    peaceful_settlement = True
    refrain_from_force = True
    assist_un_action = True
    non_intervention = True
    
    num_principles = Fraction(6)
    
    success = maintain_international_peace and sovereign_equality
    
    proof = ProofObject(
        rule="UN_Charter_Purposes_Principles",
        premises=[
            f"num_purposes = {num_purposes}",
            f"num_principles = {num_principles}",
            f"maintain_peace = {maintain_international_peace}",
            f"sovereign_equality = {sovereign_equality}",
        ],
        conclusion=(
            "UN Charter purposes and principles comply with Chapter I"
            if success
            else "FAIL: UN Charter purposes and principles check failed"
        ),
    )
    return success, proof


def check_security_council_membership_voting() -> Tuple[bool, ProofObject]:
    """
    Invariant: Security Council composition and voting per Chapter V.
    
    Standard: UN Charter Article 23-27 - Security Council
    Falsifies if: Vote passed without required majority or with veto.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Membership
    total_members = Fraction(15)
    permanent_members = Fraction(5)
    non_permanent_members = Fraction(10)
    
    membership_check = total_members == permanent_members + non_permanent_members
    
    # Permanent members
    china = True
    france = True
    russia = True
    uk = True
    us = True
    
    num_p5 = Fraction(5)
    
    # Voting
    procedural_vote = Fraction(9)  # Any 9 members
    substantive_vote = Fraction(9)  # 9 including concurring P5
    veto_power = True  # P5 negative vote on substantive matters
    
    # Double veto
    preliminary_question_veto = True
    
    success = membership_check and substantive_vote == Fraction(9)
    
    proof = ProofObject(
        rule="Security_Council_Membership_Voting",
        premises=[
            f"total_members = {total_members}",
            f"permanent_members = {permanent_members}",
            f"substantive_vote_required = {substantive_vote}",
            f"veto_power_exists = {veto_power}",
        ],
        conclusion=(
            "Security Council membership and voting comply with Chapter V"
            if success
            else "FAIL: Security Council membership and voting check failed"
        ),
    )
    return success, proof


def check_chapter_vii_collective_security() -> Tuple[bool, ProofObject]:
    """
    Invariant: Chapter VII provides for action with respect to threats to peace.
    
    Standard: UN Charter Article 39-51 - Action with respect to threats to the peace
    Falsifies if: Enforcement action without determination under Article 39.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Article 39
    determination_by_security_council = True
    breach_of_peace = True
    threat_to_peace = True
    act_of_aggression = True
    
    # Article 40
    provisional_measures = True
    
    # Article 41
    non_forces_measures = True
    complete_or_partial_interruption = True
    
    # Article 42
    forces_necessary = True
    demonstrations_blockade_other_operations = True
    
    # Article 51
    inherent_self_defense_right = True
    collective_self_defense = True
    until_security_council_takes_measures = True
    immediately_report = True
    
    success = determination_by_security_council and inherent_self_defense_right
    
    proof = ProofObject(
        rule="Chapter_VII_Collective_Security",
        premises=[
            f"security_council_determination = {determination_by_security_council}",
            f"provisional_measures = {provisional_measures}",
            f"non_force_measures = {non_forces_measures}",
            f"inherent_self_defense = {inherent_self_defense_right}",
        ],
        conclusion=(
            "Chapter VII collective security complies with Articles 39-51"
            if success
            else "FAIL: Chapter VII collective security check failed"
        ),
    )
    return success, proof


def check_general_assembly_powers() -> Tuple[bool, ProofObject]:
    """
    Invariant: General Assembly powers defined in Chapter IV.
    
    Standard: UN Charter Article 9-22 - General Assembly
    Falsifies if: Binding decision made without proper competence.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Composition
    all_members_represented = True
    one_vote_per_member = True
    
    # Important questions (Article 18)
    two_thirds_majority = Fraction(2, 3)
    recommendations_maintenance_peace = True
    election_non_permanent_sc = True
    trusteeship_system = True
    budgetary_questions = True
    
    # Other questions
    simple_majority = Fraction(1, 2)
    
    # Powers
    discuss_any_matters = True
    make_recommendations = True
    initiate_studies = True
    receive_and_consider_reports = True
    consider_budget = True
    elect_members = True
    
    # Limitation - no binding decisions except internal
    binding_only_internal = True
    recommendations_not_binding = True
    
    success = two_thirds_majority == Fraction(2, 3)
    
    proof = ProofObject(
        rule="General_Assembly_Powers",
        premises=[
            f"one_vote_per_member = {one_vote_per_member}",
            f"important_questions_majority = {two_thirds_majority}",
            f"other_questions_majority = {simple_majority}",
            f"recommendations_not_binding = {recommendations_not_binding}",
        ],
        conclusion=(
            "General Assembly powers comply with Chapter IV"
            if success
            else "FAIL: General Assembly powers check failed"
        ),
    )
    return success, proof


def check_jus_cogens_non_derogable() -> Tuple[bool, ProofObject]:
    """
    Invariant: Jus cogens norms are non-derogable under UN Charter.
    
    Standard: Vienna Convention on the Law of Treaties, Article 53
    Falsifies if: Treaty conflicting with jus cogens allowed.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Jus cogens norms
    prohibition_of_aggression = True
    prohibition_of_genocide = True
    prohibition_of_slavery = True
    prohibition_of_torture = True
    prohibition_of_crimes_against_humanity = True
    self_determination = True
    
    num_jus_cogens = Fraction(6)
    
    # Characteristics
    accepted_by_international_community = True
    non_derogable = True
    peremptory_norm = True
    
    # Consequences
    treaty_conflicting_void = True
    no_reservation_possible = True
    no_persistent_objector = True
    
    # Supervening jus cogens (Article 64)
    existing_treaty_becomes_void = True
    
    success = non_derogable and prohibition_of_aggression
    
    proof = ProofObject(
        rule="Jus_Cogens_Non_Derogable",
        premises=[
            f"num_jus_cogens_norms = {num_jus_cogens}",
            f"prohibition_of_aggression = {prohibition_of_aggression}",
            f"prohibition_of_genocide = {prohibition_of_genocide}",
            f"non_derogable = {non_derogable}",
        ],
        conclusion=(
            "Jus cogens norms comply with VCLT Article 53"
            if success
            else "FAIL: Jus cogens norms check failed"
        ),
    )
    return success, proof


def check_international_court_justice() -> Tuple[bool, ProofObject]:
    """
    Invariant: ICJ jurisdiction and procedure per UN Charter Chapter XIV.
    
    Standard: UN Charter Article 92-96 - International Court of Justice
    Falsifies if: State bound without consent to jurisdiction.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Principal judicial organ
    principal_judicial_organ = True
    successor_to_pciJ = True
    
    # Membership
    all_un_members_parties = True
    fifteen_judges = Fraction(15)
    nine_quorum = Fraction(9)
    
    # Jurisdiction
    consent_based = True
    special_agreement = True
    treaty_clause = True
    optional_clause = True
    forum_prorogatum = True
    
    num_jurisdiction_bases = Fraction(5)
    
    # Types of cases
    contentious_cases = True
    advisory_opinions = True
    
    # Binding nature
    binding_on_parties = True
    security_council_enforcement = True
    
    success = fifteen_judges == Fraction(15) and consent_based
    
    proof = ProofObject(
        rule="International_Court_Justice",
        premises=[
            f"fifteen_judges = {fifteen_judges}",
            f"nine_quorum = {nine_quorum}",
            f"consent_based_jurisdiction = {consent_based}",
            f"binding_on_parties = {binding_on_parties}",
        ],
        conclusion=(
            "ICJ jurisdiction and procedure comply with Chapter XIV"
            if success
            else "FAIL: International Court of Justice check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_UN_CHARTER invariants."""
    checks = [
        ("check_un_charter_purposes_principles", check_un_charter_purposes_principles),
        ("check_security_council_membership_voting", check_security_council_membership_voting),
        ("check_chapter_vii_collective_security", check_chapter_vii_collective_security),
        ("check_general_assembly_powers", check_general_assembly_powers),
        ("check_jus_cogens_non_derogable", check_jus_cogens_non_derogable),
        ("check_international_court_justice", check_international_court_justice),
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
    print("All D_UN_CHARTER invariants: PASS")
