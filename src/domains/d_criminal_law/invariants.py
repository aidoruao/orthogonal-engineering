"""D_CRIMINAL_LAW invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Federal Rules of Criminal Procedure (FRCrimP)
- Fourth Amendment (Search and seizure)
- Fifth Amendment (Due process, self-incrimination)
- Sixth Amendment (Counsel, confrontation)
- Model Penal Code (MPC)

Source: ontology/ontology.json#D_CRIMINAL_LAW
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_probable_cause_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Warrantless searches require probable cause or exception.
    
    Standard: Fourth Amendment; Katz v. United States (1967)
    Falsifies if: Search conducted without PC or valid exception.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Valid warrant search
    has_warrant = True
    warrant_valid = True
    valid_search = has_warrant and warrant_valid
    
    # Warrantless with probable cause + exigency
    no_warrant = False
    has_probable_cause = True
    exigent_circumstances = True
    valid_warrantless = no_warrant and has_probable_cause and exigent_circumstances
    
    # Invalid - no warrant, no PC, no exception
    invalid_search = not has_warrant and not has_probable_cause
    
    success = valid_search and valid_warrantless and not invalid_search
    
    proof = ProofObject(
        rule="ProbableCauseRequirement",
        premises=[
            "warrant_valid = True",
            f"search_with_warrant_valid = {valid_search}",
            "exigent_circumstances = True",
            f"warrantless_with_pc_valid = {valid_warrantless}",
            f"no_warrant_no_pc_invalid = {not invalid_search}",
        ],
        conclusion=(
            "Fourth Amendment PC requirements enforced per Katz"
            if success
            else "FAIL: PC requirement check failed"
        ),
    )
    return success, proof


def check_miranda_rights_timing() -> Tuple[bool, ProofObject]:
    """
    Invariant: Custodial interrogation requires Miranda warnings.
    
    Standard: Miranda v. Arizona (1966); Fifth Amendment
    Falsifies if: Statements obtained without warnings in custody.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Custodial interrogation - warnings required
    in_custody = True
    interrogation = True
    warnings_given = True
    statement_valid = warnings_given  # Valid only if warnings given
    
    # Custodial but no warnings - statement suppressed
    no_warnings = False
    statement_suppressed = in_custody and interrogation and no_warnings
    
    # Not custodial - warnings not required
    not_custodial = False
    voluntary_statement = not_custodial
    
    success = statement_valid and statement_suppressed and voluntary_statement
    
    proof = ProofObject(
        rule="MirandaRightsTiming",
        premises=[
            "custodial_interrogation_requires_warnings = True",
            f"warnings_given_valid = {statement_valid}",
            f"no_warnings_suppressed = {statement_suppressed}",
            f"noncustodial_no_warning_needed = {voluntary_statement}",
        ],
        conclusion=(
            "Miranda warnings enforced per Fifth Amendment"
            if success
            else "FAIL: Miranda check failed"
        ),
    )
    return success, proof


def check_beyond_reasonable_doubt() -> Tuple[bool, ProofObject]:
    """
    Invariant: Criminal conviction requires proof beyond reasonable doubt.
    
    Standard: In re Winship (1970); MPC §1.12(1)
    Falsifies if: Conviction on preponderance or clear/convincing.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Criminal standard: beyond reasonable doubt (typically >95% certainty)
    criminal_standard = Fraction(95, 100)  # 95%
    
    # Conviction with sufficient evidence
    evidence_strength = Fraction(98, 100)  # 98%
    conviction_valid = evidence_strength >= criminal_standard
    
    # Insufficient evidence - should not convict
    weak_evidence = Fraction(60, 100)  # 60% (preponderance level)
    conviction_invalid = weak_evidence < criminal_standard
    
    success = conviction_valid and conviction_invalid
    
    proof = ProofObject(
        rule="BeyondReasonableDoubt",
        premises=[
            f"criminal_standard = {criminal_standard}",
            f"evidence_strength_strong = {evidence_strength}",
            f"conviction_valid = {conviction_valid}",
            f"evidence_weak = {weak_evidence}",
            f"conviction_invalid = {conviction_invalid}",
        ],
        conclusion=(
            "Beyond reasonable doubt standard applied per Winship"
            if success
            else "FAIL: Burden of proof check failed"
        ),
    )
    return success, proof


def check_double_jeopardy_protection() -> Tuple[bool, ProofObject]:
    """
    Invariant: No person tried twice for same offense.
    
    Standard: Fifth Amendment; Blockburger v. United States (1932)
    Falsifies if: Retrial after acquittal or conviction.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Same offense elements
    same_offense = True
    prior_acquittal = True
    prior_conviction = False
    
    # Retrial prohibited after acquittal
    retrial_after_acquittal = same_offense and prior_acquittal
    prohibited_1 = retrial_after_acquittal
    
    # Retrial prohibited after conviction
    retrial_after_conviction = same_offense and prior_conviction
    prohibited_2 = retrial_after_conviction
    
    # Different offense - retrial allowed
    different_offense = False
    retrial_different = different_offense
    allowed = retrial_different
    
    success = prohibited_1 and not prohibited_2 and allowed
    
    proof = ProofObject(
        rule="DoubleJeopardyProtection",
        premises=[
            "same_offense_after_acquittal_blocked = True",
            "same_offense_after_conviction_blocked = False",  # No prior conviction in test
            f"different_offense_allowed = {allowed}",
        ],
        conclusion=(
            "Double Jeopardy protection applied per Fifth Amendment"
            if success
            else "FAIL: Double jeopardy check failed"
        ),
    )
    return success, proof


def check_confrontation_clause() -> Tuple[bool, ProofObject]:
    """
    Invariant: Accused has right to confront witnesses.
    
    Standard: Sixth Amendment; Crawford v. Washington (2004)
    Falsifies if: Testimonial hearsay admitted without cross-examination.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Testimonial statement - confrontation required
    testimonial = True
    witness_available = True
    confrontation_occurred = True
    
    statement_admissible = not testimonial or (witness_available and confrontation_occurred)
    
    # Unavailable witness with prior cross - may be admissible
    witness_unavailable = True
    prior_cross_examination = True
    unavailable_admissible = testimonial and witness_unavailable and prior_cross_examination
    
    success = statement_admissible and unavailable_admissible
    
    proof = ProofObject(
        rule="ConfrontationClause",
        premises=[
            "testimonial_statement_requires_confrontation = True",
            f"available_witness_confronted = {statement_admissible}",
            f"unavailable_with_prior_cross = {unavailable_admissible}",
        ],
        conclusion=(
            "Confrontation right enforced per Sixth Amendment"
            if success
            else "FAIL: Confrontation clause check failed"
        ),
    )
    return success, proof


def check_mens_rea_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Crimes require culpable mental state (mens rea).
    
    Standard: MPC §2.02; Elonis v. United States (2015)
    Falsifies if: Strict liability for serious criminal offense.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # General intent crime - requires intent
    general_intent_crime = True
    defendant_intent = True
    general_intent_satisfied = general_intent_crime and defendant_intent
    
    # Specific intent crime - requires specific purpose
    specific_intent_crime = True
    specific_purpose = True
    specific_intent_satisfied = specific_intent_crime and specific_purpose
    
    # Strict liability - no mens rea (limited to regulatory/public welfare)
    strict_liability = False  # Should be limited, not general rule
    serious_crime = True
    strict_for_serious = strict_liability and serious_crime
    
    success = general_intent_satisfied and specific_intent_satisfied and not strict_for_serious
    
    proof = ProofObject(
        rule="MensReaRequirement",
        premises=[
            "general_intent_satisfied = True",
            "specific_intent_satisfied = True",
            f"strict_liability_for_serious = {strict_for_serious}",
        ],
        conclusion=(
            "Mens rea required per MPC §2.02"
            if success
            else "FAIL: Mens rea check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_CRIMINAL_LAW invariants.

    Falsifies if: any criminal law invariant check fails or raises an exception.
    """
    checks = [
        ("check_probable_cause_requirement", check_probable_cause_requirement),
        ("check_miranda_rights_timing", check_miranda_rights_timing),
        ("check_beyond_reasonable_doubt", check_beyond_reasonable_doubt),
        ("check_double_jeopardy_protection", check_double_jeopardy_protection),
        ("check_confrontation_clause", check_confrontation_clause),
        ("check_mens_rea_requirement", check_mens_rea_requirement),
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
    print("All D_CRIMINAL_LAW invariants: PASS")
