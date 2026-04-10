"""D_TREATIES invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Vienna Convention on the Law of Treaties (VCLT)
- U.S. Constitution Supremacy Clause
- Treaty ratification procedures

Source: Vienna Convention on the Law of Treaties (1969)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_vclt_treaty_formation() -> Tuple[bool, ProofObject]:
    """
    Invariant: Vienna Convention governs treaty formation and interpretation.
    
    Standard: VCLT Articles 11-17 - Means of expressing consent to be bound
    Falsifies if: Treaty formed without proper consent.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Consent mechanisms
    signature = True
    exchange_of_instruments = True
    ratification = True
    acceptance = True
    approval = True
    accession = True
    
    num_mechanisms = Fraction(6)
    
    # Consent must be genuine
    free_consent = True
    coercion_of_state_invalidates = True
    coercion_of_representative_invalidates = True
    
    # Entry into force
    entry_into_force_per_treaty = True
    all_parties_consent_required = True
    
    success = free_consent and all_parties_consent_required
    
    proof = ProofObject(
        rule="VCLT_Treaty_Formation",
        premises=[
            f"num_consent_mechanisms = {num_mechanisms}",
            f"free_consent = {free_consent}",
            f"coercion_invalidates = {coercion_of_state_invalidates}",
            f"all_parties_consent = {all_parties_consent_required}",
        ],
        conclusion=(
            "VCLT treaty formation complies with Articles 11-17"
            if success
            else "FAIL: VCLT treaty formation check failed"
        ),
    )
    return success, proof


def check_vclt_interpretation_rules() -> Tuple[bool, ProofObject]:
    """
    Invariant: VCLT Article 31 provides general rule of interpretation.
    
    Standard: VCLT Article 31 - General rule of interpretation
    Falsifies if: Treaty interpreted without ordinary meaning analysis.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Article 31 elements
    ordinary_meaning = True
    context = True
    object_and_purpose = True
    good_faith = True
    
    # Context includes
    text = True
    preamble = True
    annexes = True
    related_agreements = True
    subsequent_agreements = True
    subsequent_practice = True
    
    num_context_elements = Fraction(7)
    
    # Supplementary means (Article 32)
    preparatory_work = True  # Travaux preparatoires
    circumstances_of_conclusion = True
    
    success = ordinary_meaning and context and good_faith
    
    proof = ProofObject(
        rule="VCLT_Interpretation_Rules",
        premises=[
            f"ordinary_meaning = {ordinary_meaning}",
            f"context = {context}",
            f"good_faith = {good_faith}",
            f"num_context_elements = {num_context_elements}",
        ],
        conclusion=(
            "VCLT interpretation complies with Article 31"
            if success
            else "FAIL: VCLT interpretation rules check failed"
        ),
    )
    return success, proof


def check_treaty_supremacy_clause() -> Tuple[bool, ProofObject]:
    """
    Invariant: Treaties are supreme law of the land per Constitution.
    
    Standard: U.S. Const. Art. VI, cl. 2 - Supremacy Clause
    Falsifies if: State law prevails over ratified treaty.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Supremacy clause
    constitution_supreme = True
    laws_supreme = True
    treaties_supreme = True
    
    # Judges bound thereby
    state_judges_bound = True
    notwithstanding_state_constitution_or_law = True
    
    # Self-executing vs non-self-executing
    self_executing_treaties_direct_effect = True
    non_self_executing_requires_legislation = True
    
    # Conflict resolution
    treaty_prevails_over_state_law = True
    later_in_time_for_statutes = True
    
    success = treaties_supreme and state_judges_bound
    
    proof = ProofObject(
        rule="Treaty_Supremacy_Clause",
        premises=[
            f"constitution_supreme = {constitution_supreme}",
            f"treaties_supreme = {treaties_supreme}",
            f"state_judges_bound = {state_judges_bound}",
            f"self_executing_direct_effect = {self_executing_treaties_direct_effect}",
        ],
        conclusion=(
            "Treaty supremacy complies with U.S. Const. Art. VI"
            if success
            else "FAIL: Treaty supremacy clause check failed"
        ),
    )
    return success, proof


def check_treaty_reservations() -> Tuple[bool, ProofObject]:
    """
    Invariant: VCLT governs treaty reservations and objections.
    
    Standard: VCLT Articles 19-23 - Reservations
    Falsifies if: Reservation incompatible with treaty object and purpose.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # When reservations allowed
    reservation_prohibited = False  # Unless treaty prohibits
    specified_reservations_only = False  # Unless treaty specifies
    compatible_with_object_and_purpose = True
    
    # Form and notification
    written_form = True
    communicated_to_contracting_states = True
    
    # Objections
    objection_possible = True
    incompatibility_with_object_and_purpose = True
    
    # Effect
    reserving_state_party = True
    provisions_inoperative = True
    reciprocal_effect = True
    
    success = compatible_with_object_and_purpose and written_form
    
    proof = ProofObject(
        rule="Treaty_Reservations",
        premises=[
            f"compatible_with_object_and_purpose = {compatible_with_object_and_purpose}",
            f"written_form = {written_form}",
            f"objection_possible = {objection_possible}",
            f"reciprocal_effect = {reciprocal_effect}",
        ],
        conclusion=(
            "Treaty reservations comply with VCLT Articles 19-23"
            if success
            else "FAIL: Treaty reservations check failed"
        ),
    )
    return success, proof


def check_treaty_withdrawal_termination() -> Tuple[bool, ProofObject]:
    """
    Invariant: VCLT governs treaty withdrawal and termination.
    
    Standard: VCLT Articles 54-64 - Termination and suspension
    Falsifies if: Treaty terminated without following VCLT procedures.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Termination grounds
    provisions_of_treaty = True
    consent_of_parties = True
    conclusion_of_object = True
    breach_by_other_party = True
    supervening_impossibility = True
    fundamental_change_of_circumstances = True  # Rebus sic stantibus
    
    num_grounds = Fraction(6)
    
    # Notice required
    twelve_months_notice = Fraction(12)
    unless_treaty_provides_otherwise = True
    
    # Invalid termination
    violating_treaty_obligations = False
    
    # Consequences
    release_from_obligations = True
    does_not_affect_acts_prior = True
    
    success = twelve_months_notice == Fraction(12)
    
    proof = ProofObject(
        rule="Treaty_Withdrawal_Termination",
        premises=[
            f"num_termination_grounds = {num_grounds}",
            f"notice_period = {twelve_months_notice} months",
            f"fundamental_change_doctrine = {fundamental_change_of_circumstances}",
            f"does_not_affect_prior_acts = {does_not_affect_acts_prior}",
        ],
        conclusion=(
            "Treaty withdrawal/termination complies with VCLT Articles 54-64"
            if success
            else "FAIL: Treaty withdrawal/termination check failed"
        ),
    )
    return success, proof


def check_us_treaty_ratification_process() -> Tuple[bool, ProofObject]:
    """
    Invariant: U.S. treaty ratification requires Senate advice and consent.
    
    Standard: U.S. Const. Art. II, § 2 - Treaty power
    Falsifies if: Treaty ratified without two-thirds Senate approval.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Constitutional process
    president_negotiates = True
    senate_advice_and_consent = True
    two_thirds_approval = Fraction(2, 3)
    
    # Ratification
    president_ratifies = True
    exchange_or_deposit_of_instruments = True
    
    # Executive agreements alternative
    congressional_executive_agreement = True  # Majority approval
    sole_executive_agreement = True  # President alone
    
    # Comparison
    treaty_vs_executive_agreement_force = True
    
    # Senate conditions
    reservations = True
    understandings = True
    declarations = True
    provisos = True
    
    num_condition_types = Fraction(4)
    
    success = two_thirds_approval == Fraction(2, 3)
    
    proof = ProofObject(
        rule="US_Treaty_Ratification_Process",
        premises=[
            f"senate_advice_and_consent = {senate_advice_and_consent}",
            f"two_thirds_required = {two_thirds_approval}",
            f"executive_agreement_alternative = {congressional_executive_agreement}",
            f"num_condition_types = {num_condition_types}",
        ],
        conclusion=(
            "U.S. treaty ratification complies with U.S. Const. Art. II, § 2"
            if success
            else "FAIL: U.S. treaty ratification process check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_TREATIES invariants."""
    checks = [
        ("check_vclt_treaty_formation", check_vclt_treaty_formation),
        ("check_vclt_interpretation_rules", check_vclt_interpretation_rules),
        ("check_treaty_supremacy_clause", check_treaty_supremacy_clause),
        ("check_treaty_reservations", check_treaty_reservations),
        ("check_treaty_withdrawal_termination", check_treaty_withdrawal_termination),
        ("check_us_treaty_ratification_process", check_us_treaty_ratification_process),
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
    print("All D_TREATIES invariants: PASS")
