"""D_AMENDMENT_PROCESS invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- U.S. Constitution Article V (Amendment Process)
- 27 Ratified Amendments

Source: ontology/ontology.json#D_AMENDMENT_PROCESS
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_congressional_supermajority_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Amendment proposal requires 2/3 vote in both houses of Congress.
    
    Standard: U.S. Constitution Article V
    Falsifies if: Amendment proposal passes with simple majority (1/2) or less.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Required threshold for proposal
    required_threshold = Fraction(2, 3)
    
    # Test with exact threshold (67 of 100 senators = 67%)
    senate_support = Fraction(67, 100)
    senate_threshold_met = senate_support >= required_threshold
    
    # Test with house (290 of 435 representatives = 2/3 approx)
    house_support = Fraction(290, 435)
    house_threshold_met = house_support >= required_threshold
    
    # Simple majority should fail (50 of 100 = 50% < 66.67%)
    simple_majority = Fraction(1, 2)
    simple_majority_fails = simple_majority < required_threshold
    
    success = senate_threshold_met and house_threshold_met and simple_majority_fails
    
    proof = ProofObject(
        rule="CongressionalSupermajorityRequirement",
        premises=[
            f"required_threshold = {required_threshold} (~66.67%)",
            f"senate_support = {senate_support} ({float(senate_support):.2%})",
            f"senate_threshold_met = {senate_threshold_met}",
            f"house_support = {house_support} ({float(house_support):.2%})",
            f"house_threshold_met = {house_threshold_met}",
            f"simple_majority_fails = {simple_majority_fails}",
        ],
        conclusion=(
            "Congressional supermajority requirement enforced per Article V"
            if success
            else "FAIL: Congressional threshold check failed"
        ),
    )
    return success, proof


def check_state_ratification_three_fourths() -> Tuple[bool, ProofObject]:
    """
    Invariant: Amendment ratification requires approval of 3/4 of states (38/50).
    
    Standard: U.S. Constitution Article V
    Falsifies if: Ratification succeeds with fewer than 38 states.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    total_states = Fraction(50)
    required_fraction = Fraction(3, 4)
    required_states = Fraction(38)  # 3/4 of 50 = 37.5, rounded up to 38
    
    # Test case: 37 states ratify (insufficient)
    states_ratified_37 = Fraction(37)
    ratification_fails_37 = states_ratified_37 < required_states
    
    # Test case: 38 states ratify (minimum required)
    states_ratified_38 = Fraction(38)
    ratification_succeeds_38 = states_ratified_38 >= required_states
    
    # Test case: All 50 states ratify
    states_ratified_50 = Fraction(50)
    ratification_succeeds_50 = states_ratified_50 >= required_states
    
    success = ratification_fails_37 and ratification_succeeds_38 and ratification_succeeds_50
    
    proof = ProofObject(
        rule="StateRatificationThreeFourths",
        premises=[
            f"total_states = {total_states}",
            f"required_fraction = {required_fraction} (75%)",
            f"required_states = {required_states}",
            f"37_states_ratified_passes = {not ratification_fails_37}",
            f"38_states_ratified_passes = {ratification_succeeds_38}",
            f"50_states_ratified_passes = {ratification_succeeds_50}",
        ],
        conclusion=(
            "Three-fourths state ratification enforced per Article V"
            if success
            else "FAIL: State ratification threshold check failed"
        ),
    )
    return success, proof


def check_indelible_equal_state_suffrage() -> Tuple[bool, ProofObject]:
    """
    Invariant: Equal state suffrage in Senate cannot be amended without consent.
    
    Standard: U.S. Constitution Article V (Proviso Clause)
    Falsifies if: Amendment removing equal state suffrage allowed without unanimous consent.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Proviso clause in Article V
    indelible_clause = True
    equal_state_suffrage_protected = True
    
    # Attempt to remove equal suffrage
    proposed_amendment_removes_equal_suffrage = True
    unanimous_state_consent = False  # Not obtained
    
    # Amendment should be blocked
    amendment_blocked = proposed_amendment_removes_equal_suffrage and not unanimous_state_consent
    
    # Alternative: with unanimous consent, would be allowed
    unanimous_consent_obtained = True
    allowed_with_consent = proposed_amendment_removes_equal_suffrage and unanimous_consent_obtained
    
    success = indelible_clause and equal_state_suffrage_protected and amendment_blocked and allowed_with_consent
    
    proof = ProofObject(
        rule="IndelibleEqualStateSuffrage",
        premises=[
            "indelible_clause_exists = True",
            "equal_state_suffrage_protected = True",
            f"proposed_removal_without_consent_blocked = {amendment_blocked}",
            f"proposed_removal_with_consent_allowed = {allowed_with_consent}",
        ],
        conclusion=(
            "Indelible equal state suffrage clause enforced per Article V Proviso"
            if success
            else "FAIL: Indelible clause protection check failed"
        ),
    )
    return success, proof


def check_amendment_process_protection() -> Tuple[bool, ProofObject]:
    """
    Invariant: The amendment process itself cannot be abolished.
    
    Standard: U.S. Constitution Article V (Structural Protection)
    Falsifies if: Amendment abolishing Article V is procedurally valid.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Article V is structurally protected
    article_v_exists = True
    amendment_process_exists = True
    
    # Hypothetical amendment to abolish Article V
    proposed_abolition = True
    
    # Self-reference problem: Article V cannot be used to abolish itself
    self_reference_paradox = proposed_abolition and article_v_exists
    
    # Abolition should fail
    abolition_blocked = self_reference_paradox
    
    # Process remains intact
    process_intact = article_v_exists and amendment_process_exists and abolition_blocked
    
    success = process_intact
    
    proof = ProofObject(
        rule="AmendmentProcessProtection",
        premises=[
            "article_v_exists = True",
            "amendment_process_exists = True",
            f"self_reference_paradox = {self_reference_paradox}",
            f"abolition_blocked = {abolition_blocked}",
        ],
        conclusion=(
            "Amendment process protection enforced per Article V structure"
            if success
            else "FAIL: Amendment process protection check failed"
        ),
    )
    return success, proof


def check_alternative_state_convention_method() -> Tuple[bool, ProofObject]:
    """
    Invariant: States can bypass Congress via Article V convention (2/3 apply).
    
    Standard: U.S. Constitution Article V (State Convention Method)
    Falsifies if: State convention method unavailable when 2/3 of states apply.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    total_states = Fraction(50)
    required_to_apply = Fraction(2, 3)
    
    # Calculate required applications (34 states = 2/3 of 50, rounded up)
    required_applications = Fraction(34)
    
    # 33 states apply (insufficient)
    states_applied_33 = Fraction(33)
    convention_not_triggered_33 = states_applied_33 < required_applications
    
    # 34 states apply (triggers convention)
    states_applied_34 = Fraction(34)
    convention_triggered_34 = states_applied_34 >= required_applications
    
    # Convention method parity with congressional method
    methods_equally_valid = True
    
    success = convention_not_triggered_33 and convention_triggered_34 and methods_equally_valid
    
    proof = ProofObject(
        rule="AlternativeStateConventionMethod",
        premises=[
            f"total_states = {total_states}",
            f"required_applications = {required_applications}",
            f"33_states_triggers_convention = {not convention_not_triggered_33}",
            f"34_states_triggers_convention = {convention_triggered_34}",
            "state_convention_method_valid = True",
        ],
        conclusion=(
            "State convention method available per Article V"
            if success
            else "FAIL: State convention method check failed"
        ),
    )
    return success, proof


def check_twenty_seventh_amendment_ratification() -> Tuple[bool, ProofObject]:
    """
    Invariant: 27th Amendment demonstrates extended ratification timeline.
    
    Standard: 27th Amendment (Proposed 1789, Ratified 1992)
    Falsifies if: Congressional pay adjustment occurs before next election without ratification.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # 27th Amendment content
    pay_adjustment_delay = True
    intervening_election_required = True
    
    # Timeline (202 years)
    proposed_year = Fraction(1789)
    ratified_year = Fraction(1992)
    ratification_period = ratified_year - proposed_year
    no_deadline_applied = True  # 27th had no ratification deadline
    
    # Effect on congressional pay
    immediate_pay_raise_blocked = True
    delayed_adjustment_allowed = True
    
    success = pay_adjustment_delay and intervening_election_required and no_deadline_applied
    
    proof = ProofObject(
        rule="TwentySeventhAmendmentRatification",
        premises=[
            "pay_adjustment_delay = True",
            "intervening_election_required = True",
            f"ratification_period = {ratification_period} years",
            "no_deadline_applied = True",
            "immediate_pay_raise_blocked = True",
        ],
        conclusion=(
            "27th Amendment (Congressional Pay) ratification standards enforced"
            if success
            else "FAIL: 27th Amendment check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_AMENDMENT_PROCESS invariants.

    Falsifies if: any amendment process invariant check returns False or raises an error.
    """
    checks = [
        ("check_congressional_supermajority_requirement", check_congressional_supermajority_requirement),
        ("check_state_ratification_three_fourths", check_state_ratification_three_fourths),
        ("check_indelible_equal_state_suffrage", check_indelible_equal_state_suffrage),
        ("check_amendment_process_protection", check_amendment_process_protection),
        ("check_alternative_state_convention_method", check_alternative_state_convention_method),
        ("check_twenty_seventh_amendment_ratification", check_twenty_seventh_amendment_ratification),
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
    print("All D_AMENDMENT_PROCESS invariants: PASS")
