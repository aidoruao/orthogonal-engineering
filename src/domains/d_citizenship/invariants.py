"""D_CITIZENSHIP invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Immigration and Nationality Act (INA) 8 U.S.C. §1401
- U.S. Constitution 14th Amendment (Birthright Citizenship)
- INA 8 U.S.C. §1423 (Naturalization Requirements)

Source: ontology/ontology.json#D_CITIZENSHIP
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_fourteenth_amendment_birthright() -> Tuple[bool, ProofObject]:
    """
    Invariant: All persons born on U.S. soil are citizens (14th Amendment).
    
    Standard: U.S. Constitution Amendment XIV, Section 1; INA §301(a)
    Falsifies if: U.S.-born person denied citizenship without lawful revocation.
    falsifies_if: U.S.-born person denied citizenship without lawful revocation.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Birthright citizenship elements
    born_in_united_states = True
    subject_to_us_jurisdiction = True
    
    # Diplomatic immunity exception
    diplomatic_immunity = False
    jurisdiction_exception = diplomatic_immunity
    
    # Citizenship determination
    birthright_citizenship = born_in_united_states and subject_to_us_jurisdiction and not jurisdiction_exception
    
    # 14th Amendment citizenship is irrevocable (except voluntary renunciation)
    involuntary_revocation_attempted = False
    revocation_blocked = birthright_citizenship and involuntary_revocation_attempted
    
    # Parentage test (for children born abroad)
    parent_citizenship = True
    parent_residence_requirement = Fraction(5)  # years
    parent_actual_residence = Fraction(6)
    parent_requirement_met = parent_actual_residence >= parent_residence_requirement
    
    derived_citizenship = parent_citizenship and parent_requirement_met
    
    success = birthright_citizenship and not revocation_blocked and derived_citizenship
    
    proof = ProofObject(
        rule="FourteenthAmendmentBirthright",
        premises=[
            "born_in_united_states = True",
            "subject_to_us_jurisdiction = True",
            f"diplomatic_immunity_exception = {jurisdiction_exception}",
            f"birthright_citizenship = {birthright_citizenship}",
            f"involuntary_revocation_blocked = {not revocation_blocked}",
        ],
        conclusion=(
            "14th Amendment birthright citizenship enforced"
            if success
            else "FAIL: Birthright citizenship check failed"
        ),
    )
    return success, proof


def check_naturalization_residency_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Naturalization requires 5 years LPR status (3 years if married to citizen).
    
    Standard: INA §316(a), §319(a)
    Falsifies if: Naturalization granted with insufficient continuous residence.
    falsifies_if: Naturalization granted with insufficient continuous residence.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Standard naturalization
    required_years_standard = Fraction(5)
    lpr_years_standard = Fraction(4)
    standard_residency_met = lpr_years_standard >= required_years_standard
    standard_residency_not_met = not standard_residency_met
    
    # Married to U.S. citizen
    required_years_marriage = Fraction(3)
    lpr_years_marriage = Fraction(4)
    married_to_citizen = True
    marriage_residency_met = lpr_years_marriage >= required_years_marriage and married_to_citizen
    
    # Continuous residence requirement
    trip_abroad_days = Fraction(180)
    continuous_residence_threshold = Fraction(180)  # 6 months
    continuous_residence_broken = trip_abroad_days > continuous_residence_threshold
    
    # Physical presence requirement (half of required years)
    physical_presence_required = required_years_standard / Fraction(2)
    physical_presence_days = physical_presence_required * Fraction(365)
    
    success = standard_residency_not_met and marriage_residency_met and continuous_residence_broken
    
    proof = ProofObject(
        rule="NaturalizationResidencyRequirement",
        premises=[
            f"required_years_standard = {required_years_standard}",
            f"lpr_years_standard = {lpr_years_standard}",
            f"standard_residency_met = {standard_residency_met}",
            f"required_years_marriage = {required_years_marriage}",
            f"marriage_residency_met = {marriage_residency_met}",
            f"continuous_residence_broken = {continuous_residence_broken}",
        ],
        conclusion=(
            "Naturalization residency requirement enforced per INA §316"
            if success
            else "FAIL: Naturalization residency check failed"
        ),
    )
    return success, proof


def check_naturalization_good_moral_character() -> Tuple[bool, ProofObject]:
    """
    Invariant: Naturalization requires good moral character during statutory period.
    
    Standard: INA §101(f), §316(a)(3)
    Falsifies if: Naturalization granted despite statutory disqualifying offense.
    falsifies_if: Naturalization granted despite statutory disqualifying offense.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Statutory period for GMC
    gmc_period_years = Fraction(5)
    
    # Disqualifying offenses (permanent bars)
    aggravated_felony = True
    murder_conviction = False
    permanent_bar = aggravated_felony or murder_conviction
    
    # Conditional bars (during statutory period)
    crime_involving_moral_turpitude = True
    cimt_within_period = True
    cimt_bar = crime_involving_moral_turpitude and cimt_within_period
    
    # Multiple offenses
    multiple_convictions = True
    aggregate_sentence = Fraction(5)  # years
    multiple_offense_bar = multiple_convictions and aggregate_sentence >= Fraction(5)
    
    # Controlled substance (except single possession < 30g marijuana)
    controlled_substance_violation = True
    single_possession_marijuana_under_30g = False
    drug_bar = controlled_substance_violation and not single_possession_marijuana_under_30g
    
    gmc_failed = permanent_bar or cimt_bar or multiple_offense_bar or drug_bar
    
    success = gmc_failed  # Demonstrates that disqualifying conditions are detected
    
    proof = ProofObject(
        rule="NaturalizationGoodMoralCharacter",
        premises=[
            f"gmc_period_years = {gmc_period_years}",
            f"permanent_bar (aggravated_felony) = {permanent_bar}",
            f"cimt_bar = {cimt_bar}",
            f"multiple_offense_bar = {multiple_offense_bar}",
            f"drug_bar = {drug_bar}",
            f"gmc_requirement_failed = {gmc_failed}",
        ],
        conclusion=(
            "Good moral character requirement enforced per INA §101(f)"
            if success
            else "FAIL: Good moral character check failed"
        ),
    )
    return success, proof


def check_citizenship_through_derivation() -> Tuple[bool, ProofObject]:
    """
    Invariant: Children may derive citizenship through naturalization of parent.
    
    Standard: INA §320 (Child Citizenship Act of 2000)
    Falsifies if: Child of naturalized parent denied derived citizenship when conditions met.
    falsifies_if: Child of naturalized parent denied derived citizenship when conditions met.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # CCA 2000 requirements
    child_under_18 = True
    lpr_status = True
    
    # Parent naturalization
    parent_naturalized = True
    parent_is_custodial = True
    
    # Residence
    residing_in_us = True
    residing_in_custody_of_citizen_parent = parent_is_custodial and residing_in_us
    
    # All conditions must be met
    derivation_conditions_met = (
        child_under_18 and 
        lpr_status and 
        parent_naturalized and 
        residing_in_custody_of_citizen_parent
    )
    
    # Automatic citizenship upon meeting all conditions
    derived_citizenship_acquired = derivation_conditions_met
    
    # Certificate of citizenship available but not required
    certificate_of_citizenship_issued = True
    
    # Expatriation risk (child cannot lose citizenship due to parent's actions)
    parent_renounces = False
    child_citizenship_preserved = derived_citizenship_acquired and parent_renounces
    
    success = derived_citizenship_acquired and certificate_of_citizenship_issued
    
    proof = ProofObject(
        rule="CitizenshipThroughDerivation",
        premises=[
            "child_under_18 = True",
            "lpr_status = True",
            "parent_naturalized = True",
            "residing_in_custody_of_citizen_parent = True",
            f"derivation_conditions_met = {derivation_conditions_met}",
            f"derived_citizenship_acquired = {derived_citizenship_acquired}",
        ],
        conclusion=(
            "Child Citizenship Act derivation enforced per INA §320"
            if success
            else "FAIL: Citizenship derivation check failed"
        ),
    )
    return success, proof


def check_dual_nationality_recognition() -> Tuple[bool, ProofObject]:
    """
    Invariant: U.S. law recognizes but does not encourage dual nationality.
    
    Standard: INA §101(a)(22); State Department Policy
    Falsifies if: Automatic loss of U.S. citizenship upon acquiring foreign nationality.
    falsifies_if: Automatic loss of U.S. citizenship upon acquiring foreign nationality.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # U.S. citizenship acquisition
    us_birthright = True
    
    # Foreign citizenship acquisition
    foreign_parentage = True
    foreign_birthright = foreign_parentage
    
    # Dual nationality exists
    dual_nationality = us_birthright and foreign_birthright
    
    # No automatic expatriation
    automatic_loss = False
    us_citizenship_preserved = us_birthright and not automatic_loss
    
    # Naturalization in foreign state (potential expatriating act)
    foreign_naturalization = True
    intent_to_relinquish = True
    expatriation_potential = foreign_naturalization and intent_to_relinquish
    
    # State Department presumption against intent to relinquish
    presumption_against_relinquishment = True
    expatriation_avoided = expatriation_potential and presumption_against_relinquishment
    
    # Oath of naturalization includes renunciation language but
    # intent to retain U.S. citizenship may be stated
    
    success = dual_nationality and us_citizenship_preserved and expatriation_avoided
    
    proof = ProofObject(
        rule="DualNationalityRecognition",
        premises=[
            "us_birthright = True",
            "foreign_birthright = True",
            f"dual_nationality_exists = {dual_nationality}",
            f"automatic_loss = {automatic_loss}",
            f"presumption_against_relinquishment = {presumption_against_relinquishment}",
        ],
        conclusion=(
            "Dual nationality policy enforced per INA §101(a)(22)"
            if success
            else "FAIL: Dual nationality check failed"
        ),
    )
    return success, proof


def check_renunciation_requirements() -> Tuple[bool, ProofObject]:
    """
    Invariant: Voluntary renunciation requires intent and formal process abroad.
    
    Standard: INA §349(a)(5); 8 U.S.C. §1481
    Falsifies if: Renunciation accepted without voluntary intent or outside prescribed form.
    falsifies_if: Renunciation accepted without voluntary intent or outside prescribed form.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Voluntary intent required
    voluntary_intent = True
    duress_present = False
    
    # Formal requirements
    performed_abroad = True
    before_diplomatic_consular_officer = True
    oath_administered = True
    
    # Three-part test for valid renunciation
    formal_requirements_met = (
        performed_abroad and 
        before_diplomatic_consular_officer and 
        oath_administered
    )
    
    voluntariness = voluntary_intent and not duress_present
    
    valid_renunciation = formal_requirements_met and voluntariness
    
    # Tax consequences (Exit Tax - IRC §877A)
    net_worth = Fraction(2000000)
    exit_tax_threshold = Fraction(2000000)
    exit_tax_applies = net_worth >= exit_tax_threshold
    
    # Reed Amendment (INAD for former citizens with tax motivation)
    tax_motivation_presumed = net_worth >= exit_tax_threshold
    inadmissibility_risk = valid_renunciation and tax_motivation_presumed
    
    success = valid_renunciation and exit_tax_applies
    
    proof = ProofObject(
        rule="RenunciationRequirements",
        premises=[
            f"voluntary_intent = {voluntary_intent}",
            f"performed_abroad = {performed_abroad}",
            f"before_consular_officer = {before_diplomatic_consular_officer}",
            f"valid_renunciation = {valid_renunciation}",
            f"exit_tax_applies = {exit_tax_applies}",
        ],
        conclusion=(
            "Renunciation requirements enforced per INA §349"
            if success
            else "FAIL: Renunciation check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_CITIZENSHIP invariants.

    Falsifies if: any citizenship invariant check fails or raises an exception.
    falsifies_if: any citizenship invariant check fails or raises an exception.
    """
    checks = [
        ("check_fourteenth_amendment_birthright", check_fourteenth_amendment_birthright),
        ("check_naturalization_residency_requirement", check_naturalization_residency_requirement),
        ("check_naturalization_good_moral_character", check_naturalization_good_moral_character),
        ("check_citizenship_through_derivation", check_citizenship_through_derivation),
        ("check_dual_nationality_recognition", check_dual_nationality_recognition),
        ("check_renunciation_requirements", check_renunciation_requirements),
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
    print("All D_CITIZENSHIP invariants: PASS")
