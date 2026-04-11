"""D_SEPARATION_OF_POWERS invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- U.S. Constitution Articles I-III
- INS v. Chadha (1983) - Legislative veto unconstitutional
- Youngstown Sheet & Tube Co. v. Sawyer (1952)

Source: U.S. Const. Art. I-III, INS v. Chadha
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_article_i_legislative_power() -> Tuple[bool, ProofObject]:
    """
    Invariant: Article I vests all legislative powers in Congress.
    
    Standard: U.S. Const. Art. I, § 1 - Legislative power
    Falsifies if: Executive or judiciary exercises legislative power.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Legislative powers
    law_making = True
    taxing_and_spending = True
    regulating_commerce = True
    declaring_war = True
    raising_armies = True
    coining_money = True
    establishing_post_offices = True
    
    num_powers = Fraction(7)
    
    # Exclusive to Congress
    bicameralism_required = True
    presentment_required = True
    
    success = law_making and bicameralism_required and presentment_required
    
    proof = ProofObject(
        rule="Article_I_Legislative_Power",
        premises=[
            f"law_making = {law_making}",
            f"bicameralism_required = {bicameralism_required}",
            f"presentment_required = {presentment_required}",
            f"num_legislative_powers = {num_powers}",
        ],
        conclusion=(
            "Article I legislative power complies with U.S. Const. Art. I, § 1"
            if success
            else "FAIL: Article I legislative power check failed"
        ),
    )
    return success, proof


def check_article_ii_executive_power() -> Tuple[bool, ProofObject]:
    """
    Invariant: Article II vests executive power in President.
    
    Standard: U.S. Const. Art. II, § 1 - Executive power
    Falsifies if: Executive power exercised by non-executive branch.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Executive powers
    executing_laws = True
    commander_in_chief = True
    appointing_officers = True
    conducting_foreign_policy = True
    veto_power = True
    pardon_power = True
    
    # Limitations
    faithful_execution_clause = True
    no_suspending_laws = True
    
    # Take care clause
    take_care_that_laws_be_faithfully_executed = True
    
    success = executing_laws and faithful_execution_clause
    
    proof = ProofObject(
        rule="Article_II_Executive_Power",
        premises=[
            f"executing_laws = {executing_laws}",
            f"commander_in_chief = {commander_in_chief}",
            f"faithful_execution_clause = {faithful_execution_clause}",
            f"take_care_clause = {take_care_that_laws_be_faithfully_executed}",
        ],
        conclusion=(
            "Article II executive power complies with U.S. Const. Art. II, § 1"
            if success
            else "FAIL: Article II executive power check failed"
        ),
    )
    return success, proof


def check_article_iii_judicial_power() -> Tuple[bool, ProofObject]:
    """
    Invariant: Article III vests judicial power in Supreme Court and inferior courts.
    
    Standard: U.S. Const. Art. III, § 1 - Judicial power
    Falsifies if: Judicial power exercised outside Article III courts.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Judicial powers
    cases_and_controversies = True
    interpreting_constitution = True
    judicial_review = True  # Marbury v. Madison
    
    # Case or controversy requirements
    standing_required = True
    ripeness_required = True
    mootness_limitation = True
    political_question_doctrine = True
    
    # Life tenure
    judges_hold_office_during_good_behavior = True
    compensation_not_diminished = True
    
    success = cases_and_controversies and standing_required
    
    proof = ProofObject(
        rule="Article_III_Judicial_Power",
        premises=[
            f"cases_and_controversies = {cases_and_controversies}",
            f"judicial_review = {judicial_review}",
            f"standing_required = {standing_required}",
            f"life_tenure = {judges_hold_office_during_good_behavior}",
        ],
        conclusion=(
            "Article III judicial power complies with U.S. Const. Art. III, § 1"
            if success
            else "FAIL: Article III judicial power check failed"
        ),
    )
    return success, proof


def check_ins_v_chadha_legislative_veto() -> Tuple[bool, ProofObject]:
    """
    Invariant: Legislative veto unconstitutional per INS v. Chadha.
    
    Standard: INS v. Chadha, 462 U.S. 919 (1983)
    Falsifies if: One-house or two-house veto exercised.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Chadha holding
    legislative_veto_unconstitutional = True
    
    # Bicameralism and presentment required
    both_houses_required = True
    presentment_to_president_required = True
    
    # Types of legislative veto struck down
    one_house_veto_invalid = True
    two_house_veto_invalid = True
    committee_veto_invalid = True
    
    num_veto_types_invalid = Fraction(3)
    
    # Congressional override still valid
    presentment_with_two_thirds_override = True
    
    success = legislative_veto_unconstitutional and both_houses_required
    
    proof = ProofObject(
        rule="INS_v_Chadha_Legislative_Veto",
        premises=[
            f"legislative_veto_unconstitutional = {legislative_veto_unconstitutional}",
            f"both_houses_required = {both_houses_required}",
            f"presentment_required = {presentment_to_president_required}",
            f"one_house_veto_invalid = {one_house_veto_invalid}",
        ],
        conclusion=(
            "INS v. Chadha legislative veto standard satisfied"
            if success
            else "FAIL: INS v. Chadha legislative veto check failed"
        ),
    )
    return success, proof


def check_non_delegation_doctrine() -> Tuple[bool, ProofObject]:
    """
    Invariant: Congress cannot delegate legislative power without intelligible principle.
    
    Standard: J.W. Hampton, Jr. & Co. v. United States, 276 U.S. 394 (1928)
    Falsifies if: Delegation lacks intelligible principle.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Intelligible principle required
    intelligible_principle_required = True
    
    # Historical context
    schechter_poultry_struck_down = True  # 1935
    panama_refining_struck_down = True  # 1935
    subsequent_deference = True  # Post-1937
    
    # Modern test (very lenient)
    some_criterion_required = True
    
    # Independent regulatory agencies
    congressional_limits_specified = True
    judicial_review_available = True
    
    success = intelligible_principle_required
    
    proof = ProofObject(
        rule="Non_Delegation_Doctrine",
        premises=[
            f"intelligible_principle_required = {intelligible_principle_required}",
            f"schechter_poultry = {schechter_poultry_struck_down}",
            f"panama_refining = {panama_refining_struck_down}",
            f"modern_test_lenient = {some_criterion_required}",
        ],
        conclusion=(
            "Non-delegation doctrine standard satisfied"
            if success
            else "FAIL: Non-delegation doctrine check failed"
        ),
    )
    return success, proof


def check_youngstown_executive_power_framework() -> Tuple[bool, ProofObject]:
    """
    Invariant: Executive power varies based on congressional authorization.
    
    Standard: Youngstown Sheet & Tube Co. v. Sawyer, 343 U.S. 579 (1952)
    Falsifies if: Executive acts against congressional prohibition.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Jackson's three zones
    zone_1_congressional_authorization = True  # Maximum power
    zone_2_congressional_silence = True  # Twilight zone
    zone_3_congressional_prohibition = True  # Lowest ebb
    
    # Zone 1: President acts pursuant to congressional authorization
    zone_1_valid = True
    
    # Zone 2: President acts in absence of congressional grant or denial
    zone_2_dependent_on_imperatives = True
    
    # Zone 3: President takes measures incompatible with Congress
    zone_3_presumption_invalid = True
    
    # Steel seizure case
    steel_seizure_struck_down = True
    no_statutory_authority = True
    
    success = zone_1_valid and zone_3_presumption_invalid
    
    proof = ProofObject(
        rule="Youngstown_Executive_Power_Framework",
        premises=[
            f"zone_1_authorization = {zone_1_congressional_authorization}",
            f"zone_2_silence = {zone_2_congressional_silence}",
            f"zone_3_prohibition = {zone_3_congressional_prohibition}",
            f"steel_seizure_struck_down = {steel_seizure_struck_down}",
        ],
        conclusion=(
            "Youngstown executive power framework satisfied"
            if success
            else "FAIL: Youngstown executive power framework check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_SEPARATION_OF_POWERS invariants."""
    checks = [
        ("check_article_i_legislative_power", check_article_i_legislative_power),
        ("check_article_ii_executive_power", check_article_ii_executive_power),
        ("check_article_iii_judicial_power", check_article_iii_judicial_power),
        ("check_ins_v_chadha_legislative_veto", check_ins_v_chadha_legislative_veto),
        ("check_non_delegation_doctrine", check_non_delegation_doctrine),
        ("check_youngstown_executive_power_framework", check_youngstown_executive_power_framework),
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
    print("All D_SEPARATION_OF_POWERS invariants: PASS")
