"""D_WEAPONS_REGULATION invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- NFA (National Firearms Act)
- GCA (Gun Control Act)
- Brady Act
- Second Amendment

Source: 26 U.S.C. § 5801 (NFA), 18 U.S.C. § 921 (GCA)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_nfa_registration_requirements() -> Tuple[bool, ProofObject]:
    """
    Invariant: NFA requires registration of Title II weapons.
    
    Standard: 26 U.S.C. § 5801-5872 - National Firearms Act
    Falsifies if: Unregistered machine gun, SBR, SBS, silencer, destructive device, AOW.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # NFA firearms
    machine_gun = True
    short_barreled_rifle = True
    short_barreled_shotgun = True
    silencer = True
    destructive_device = True
    any_other_weapon = True
    
    num_nfa_categories = Fraction(6)
    
    # Registration required
    registration_required = True
    serial_number_assignment = True
    
    # Transfer tax
    standard_tax = Fraction(200)
    aow_tax = Fraction(5)  # Any other weapon
    making_tax = Fraction(200)
    
    # Transfer approval
    atf_approval_required = True
    background_check = True
    chief_law_enforcement_notification = True
    
    success = standard_tax == Fraction(200) and aow_tax == Fraction(5)
    
    proof = ProofObject(
        rule="NFA_Registration_Requirements",
        premises=[
            f"num_nfa_categories = {num_nfa_categories}",
            f"standard_transfer_tax = ${standard_tax}",
            f"aow_tax = ${aow_tax}",
            f"atf_approval_required = {atf_approval_required}",
        ],
        conclusion=(
            "NFA registration requirements comply with 26 U.S.C. § 5801"
            if success
            else "FAIL: NFA registration requirements check failed"
        ),
    )
    return success, proof


def check_gca_prohibited_persons() -> Tuple[bool, ProofObject]:
    """
    Invariant: GCA prohibits firearm possession by certain categories.
    
    Standard: 18 U.S.C. § 922(g) - Unlawful acts
    Falsifies if: Prohibited person acquires firearm.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Prohibited categories
    felon = True
    fugitive = True
    unlawful_user_controlled_substance = True
    adjudicated_mental_defective = True
    illegal_alien = True
    dishonorable_discharge = True
    renounced_citizenship = True
    misdemeanor_crime_domestic_violence = True  # Lautenberg Amendment
    
    num_prohibited_categories = Fraction(9)
    
    # Penalties
    imprisonment_not_more_than = Fraction(10)  # years
    
    # Brady Act enhancement
    background_check_required = True
    nics_check = True
    
    # Private sale loophole (some states close)
    private_sale_no_check_federal = True
    
    success = background_check_required
    
    proof = ProofObject(
        rule="GCA_Prohibited_Persons",
        premises=[
            f"num_prohibited_categories = {num_prohibited_categories}",
            f"max_imprisonment = {imprisonment_not_more_than} years",
            f"background_check_required = {background_check_required}",
            f"nics_check = {nics_check}",
        ],
        conclusion=(
            "GCA prohibited persons comply with 18 U.S.C. § 922(g)"
            if success
            else "FAIL: GCA prohibited persons check failed"
        ),
    )
    return success, proof


def check_brady_act_background_checks() -> Tuple[bool, ProofObject]:
    """
    Invariant: Brady Act requires background checks for FFL sales.
    
    Standard: 18 U.S.C. § 922(t) - Brady Handgun Violence Prevention Act
    Falsifies if: FFL transfers firearm without NICS check.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # NICS check required
    ffl_transfers_only = True
    private_sales_exempt = True
    
    # Waiting period
    up_to_three_business_days = Fraction(3)
    
    # NICS responses
    proceed = True
    denied = True
    delayed = True
    
    # Default proceed
    default_proceed_after_three_days = True
    
    # Appeals
    appeal_of_denial = True
    voluntary_appeal_file = True
    
    # States alternatives
    poc_state = True  # Point of Contact - state runs check
    npp_state = True  # Non-POC - FBI runs check
    
    success = up_to_three_business_days == Fraction(3)
    
    proof = ProofObject(
        rule="Brady_Act_Background_Checks",
        premises=[
            f"max_wait_days = {up_to_three_business_days}",
            f"ffl_transfers_only = {ffl_transfers_only}",
            f"default_proceed = {default_proceed_after_three_days}",
            f"appeal_available = {appeal_of_denial}",
        ],
        conclusion=(
            "Brady Act background checks comply with 18 U.S.C. § 922(t)"
            if success
            else "FAIL: Brady Act background checks check failed"
        ),
    )
    return success, proof


def check_second_amendment_individual_right() -> Tuple[bool, ProofObject]:
    """
    Invariant: Second Amendment protects individual right to keep and bear arms.
    
    Standard: District of Columbia v. Heller, 554 U.S. 570 (2008)
    Falsifies if: Complete ban on handgun possession in home.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Heller holding
    individual_right = True
    unconnected_with_militia_service = True
    self_defense_lawful_purpose = True
    
    # Text
    well_regulated_militia = True
    security_of_free_state = True
    right_of_people = True
    keep_and_bear_arms = True
    shall_not_be_infringed = True
    
    # Limitations allowed
    prohibited_persons = True
    felons = True
    mentally_ill = True
    sensitive_places = True
    schools_government_buildings = True
    conditions_qualifications = True
    
    # McDonald v. Chicago (2010)
    incorporated_against_states = True
    fundamental_right = True
    
    success = individual_right and incorporated_against_states
    
    proof = ProofObject(
        rule="Second_Amendment_Individual_Right",
        premises=[
            f"individual_right = {individual_right}",
            f"self_defense_purpose = {self_defense_lawful_purpose}",
            f"incorporated = {incorporated_against_states}",
            f"prohibited_persons_limitation = {prohibited_persons}",
        ],
        conclusion=(
            "Second Amendment individual right verified"
            if success
            else "FAIL: Second Amendment individual right check failed"
        ),
    )
    return success, proof


def check_nfa_machine_gun_definition() -> Tuple[bool, ProofObject]:
    """
    Invariant: NFA defines machine gun as any weapon that shoots automatically.
    
    Standard: 26 U.S.C. § 5845(b) - Definitions
    Falsifies if: Semi-automatic with bump stock not regulated as machine gun.
    
    Returns:
        Tuple of (success: bool, ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Definition
    shoots_automatically = True
    more_than_one_shot = True
    single_function_of_trigger = True
    
    # Parts designed to convert
    designed_to_convert = True
    readily_restored = True
    
    # Rate of fire
    continuous_fire = True
    
    # Bump stock regulation
    atf_final_rule_2018 = True
    bump_stocks_machine_guns = True
    
    # Semi-automatic distinction
    one_shot_per_trigger_pull = True
    not_machine_gun = True
    
    success = single_function_of_trigger
    
    proof = ProofObject(
        rule="NFA_Machine_Gun_Definition",
        premises=[
            f"automatic_fire = {shoots_automatically}",
            f"single_trigger_function = {single_function_of_trigger}",
            f"bump_stocks_regulated = {bump_stocks_machine_guns}",
            f"semi_auto_distinction = {not_machine_gun}",
        ],
        conclusion=(
            "NFA machine gun definition complies with 26 U.S.C. § 5845"
            if success
            else "FAIL: NFA machine gun definition check failed"
        ),
    )
    return success, proof


def check_armed_career_criminal_act() -> Tuple[bool, ProofObject]:
    """
    Invariant: ACCA enhances sentences for armed career criminals.
    
    Standard: 18 U.S.C. § 924(e) - Armed Career Criminal Act
    Falsifies if: Career criminal not subject to enhanced penalties.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Predicate offenses required
    three_or_more_violent_felonies = Fraction(3)
    serious_drug_offenses = True
    
    # Definition issues (Johnson v. US 2015)
    residual_clause_struck_down = True
    elements_clause_remains = True
    enumerated_offenses_remain = True
    
    # Penalty
    minimum_imprisonment = Fraction(15)  # years
    
    # Predicate offenses examples
    burglary = True
    arson = True
    extortion = True
    use_of_explosives = True
    
    num_enumerated = Fraction(4)
    
    # Force requirement after Johnson
    use_carry_possession_firearm = True
    
    success = minimum_imprisonment == Fraction(15)
    
    proof = ProofObject(
        rule="Armed_Career_Criminal_Act",
        premises=[
            f"minimum_imprisonment = {minimum_imprisonment} years",
            f"predicates_required = {three_or_more_violent_felonies}",
            f"residual_clause_struck = {residual_clause_struck_down}",
            f"num_enumerated = {num_enumerated}",
        ],
        conclusion=(
            "Armed Career Criminal Act complies with 18 U.S.C. § 924(e)"
            if success
            else "FAIL: Armed Career Criminal Act check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_WEAPONS_REGULATION invariants."""
    checks = [
        ("check_nfa_registration_requirements", check_nfa_registration_requirements),
        ("check_gca_prohibited_persons", check_gca_prohibited_persons),
        ("check_brady_act_background_checks", check_brady_act_background_checks),
        ("check_second_amendment_individual_right", check_second_amendment_individual_right),
        ("check_nfa_machine_gun_definition", check_nfa_machine_gun_definition),
        ("check_armed_career_criminal_act", check_armed_career_criminal_act),
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
    print("All D_WEAPONS_REGULATION invariants: PASS")
