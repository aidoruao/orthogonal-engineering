"""D_FEDERALISM invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- U.S. Constitution, Articles I, II, III (separation of powers)
- Article VI, Clause 2 (Supremacy Clause)
- Tenth Amendment (reserved powers)

Source: ontology/ontology.json#D_FEDERALISM
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from src.domains.d_federalism.implementation import (
    FederalismChecker,
    GovernmentLevel,
    PowerType,
    SupremacyClause,
    FEDERAL_POWERS,
    STATE_POWERS,
    CONCURRENT_POWERS,
)


def check_federal_enumerated_powers() -> Tuple[bool, ProofObject]:
    """
    Invariant: Federal government may only exercise enumerated powers.
    
    Standard: U.S. Constitution Article I, Section 8
    Falsifies if: Federal government exercises non-enumerated, non-concurrent power.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = FederalismChecker()
    
    # Enumerated power: regulate interstate commerce
    commerce_result = checker.check_federal_power(
        power=PowerType.REGULATE_INTERSTATE_COMMERCE,
        description="Regulating interstate commerce",
    )
    
    # Reserved state power: education (10th Amendment)
    education_result = checker.check_federal_power(
        power=PowerType.EDUCATION,
        description="Federal education mandate",
    )
    
    # Federal can exercise enumerated powers
    enumerated_valid = commerce_result is True
    # Federal cannot exercise reserved state powers
    reserved_blocked = education_result is False
    
    success = enumerated_valid and reserved_blocked
    
    proof = ProofObject(
        rule="FederalEnumeratedPowers",
        premises=[
            f"commerce_power_exercise = {commerce_result}",
            f"education_power_exercise = {education_result}",
            f"enumerated_valid = {enumerated_valid}",
            f"reserved_blocked = {reserved_blocked}",
        ],
        conclusion=(
            "Federal enumerated powers and 10th Amendment limits enforced"
            if success
            else "FAIL: Federal power limits violated"
        ),
    )
    return success, proof


def check_tenth_amendment_reserved_powers() -> Tuple[bool, ProofObject]:
    """
    Invariant: Powers not delegated to federal government are reserved to states.
    
    Standard: U.S. Constitution Tenth Amendment
    Falsifies if: State exercise of reserved power is blocked.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = FederalismChecker()
    
    # State police power (reserved)
    police_result = checker.check_state_power(
        power=PowerType.POLICE_POWER,
        description="State police enforcing local laws",
    )
    
    # State education power (reserved)
    education_result = checker.check_state_power(
        power=PowerType.EDUCATION,
        description="State education curriculum",
    )
    
    # Both should be allowed
    police_valid = police_result is True
    education_valid = education_result is True
    
    success = police_valid and education_valid
    
    proof = ProofObject(
        rule="TenthAmendmentReservedPowers",
        premises=[
            f"police_power = {police_result}",
            f"education_power = {education_result}",
            f"reserved_powers_exercisable = {success}",
        ],
        conclusion=(
            "10th Amendment reserved powers protected"
            if success
            else "FAIL: Reserved state powers blocked"
        ),
    )
    return success, proof


def check_supremacy_clause_preemption() -> Tuple[bool, ProofObject]:
    """
    Invariant: Federal law preempts conflicting state law.
    
    Standard: U.S. Constitution Article VI, Clause 2 (Supremacy Clause)
    Falsifies if: State law prevails over valid conflicting federal law.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = FederalismChecker()
    
    resolution = checker.check_supremacy(
        federal_law="Federal Environmental Standard",
        state_law="State Environmental Standard (weaker)",
        conflict_description="State standard conflicts with federal",
    )
    
    supremacy_applies = resolution["supremacy_applies"] is True
    federal_prevails = resolution["prevailing_law"] == "Federal Environmental Standard"
    state_invalid = resolution["state_law_invalid"] is True
    
    success = supremacy_applies and federal_prevails and state_invalid
    
    proof = ProofObject(
        rule="SupremacyClausePreemption",
        premises=[
            f"supremacy_applies = {supremacy_applies}",
            f"federal_prevails = {federal_prevails}",
            f"state_law_invalid = {state_invalid}",
        ],
        conclusion=(
            "Article VI Supremacy Clause enforced"
            if success
            else "FAIL: Supremacy Clause not applied"
        ),
    )
    return success, proof


def check_concurrent_powers_exercisable() -> Tuple[bool, ProofObject]:
    """
    Invariant: Concurrent powers may be exercised by both federal and state governments.
    
    Standard: Constitutional concurrent powers (taxation, establishing courts)
    Falsifies if: Either level is blocked from exercising concurrent power.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = FederalismChecker()
    
    # Federal taxation
    fed_tax = checker.check_federal_power(
        power=PowerType.TAXATION,
        description="Federal income tax",
    )
    
    # State taxation
    state_tax = checker.check_state_power(
        power=PowerType.TAXATION,
        description="State sales tax",
    )
    
    # Federal courts
    fed_courts = checker.check_federal_power(
        power=PowerType.ESTABLISH_COURTS,
        description="Federal district courts",
    )
    
    # State courts
    state_courts = checker.check_state_power(
        power=PowerType.ESTABLISH_COURTS,
        description="State court system",
    )
    
    fed_valid = fed_tax is True and fed_courts is True
    state_valid = state_tax is True and state_courts is True
    
    success = fed_valid and state_valid
    
    proof = ProofObject(
        rule="ConcurrentPowersExercisable",
        premises=[
            f"federal_concurrent_valid = {fed_valid}",
            f"state_concurrent_valid = {state_valid}",
            f"taxation_exercisable = {fed_tax and state_tax}",
            f"courts_exercisable = {fed_courts and state_courts}",
        ],
        conclusion=(
            "Concurrent powers exercisable by both levels"
            if success
            else "FAIL: Concurrent powers blocked"
        ),
    )
    return success, proof


def check_tenth_amendment_violation_detection() -> Tuple[bool, ProofObject]:
    """
    Invariant: Federal overreach into reserved powers violates 10th Amendment.
    
    Standard: U.S. Constitution Tenth Amendment
    Falsifies if: Federal police power over local crimes not flagged as violation.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    checker = FederalismChecker()
    
    violation = checker.is_tenth_amendment_violation(
        federal_action="Federal police force for local crimes",
        power_type=PowerType.POLICE_POWER,
    )
    
    # Federal police power over local crimes should violate 10th Amendment
    violation_detected = violation is True
    
    success = violation_detected
    
    proof = ProofObject(
        rule="TenthAmendmentViolationDetection",
        premises=[
            f"federal_action = 'Federal police force for local crimes'",
            f"power_type = POLICE_POWER",
            f"violation_detected = {violation_detected}",
        ],
        conclusion=(
            "10th Amendment violation correctly detected"
            if success
            else "FAIL: 10th Amendment violation not detected"
        ),
    )
    return success, proof


def check_power_category_assignments() -> Tuple[bool, ProofObject]:
    """
    Invariant: Powers are correctly categorized as federal, state, or concurrent.
    
    Standard: Constitutional power distribution
    Falsifies if: Powers are misclassified between categories.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Check federal enumerated powers
    commerce_in_federal = PowerType.REGULATE_INTERSTATE_COMMERCE in FEDERAL_POWERS
    war_in_federal = PowerType.DECLARE_WAR in FEDERAL_POWERS
    
    # Check state reserved powers
    police_in_state = PowerType.POLICE_POWER in STATE_POWERS
    education_in_state = PowerType.EDUCATION in STATE_POWERS
    
    # Check concurrent powers
    tax_concurrent = PowerType.TAXATION in CONCURRENT_POWERS
    courts_concurrent = PowerType.ESTABLISH_COURTS in CONCURRENT_POWERS
    
    # Verify no overlap errors
    commerce_not_state = PowerType.REGULATE_INTERSTATE_COMMERCE not in STATE_POWERS
    police_not_federal = PowerType.POLICE_POWER not in FEDERAL_POWERS
    
    success = (
        commerce_in_federal and war_in_federal and
        police_in_state and education_in_state and
        tax_concurrent and courts_concurrent and
        commerce_not_state and police_not_federal
    )
    
    proof = ProofObject(
        rule="PowerCategoryAssignments",
        premises=[
            f"federal_powers_correct = {commerce_in_federal and war_in_federal}",
            f"state_powers_correct = {police_in_state and education_in_state}",
            f"concurrent_powers_correct = {tax_concurrent and courts_concurrent}",
            f"no_category_overlap = {commerce_not_state and police_not_federal}",
        ],
        conclusion=(
            "Power categories correctly assigned"
            if success
            else "FAIL: Power categories misassigned"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_FEDERALISM invariants."""
    checks = [
        ("check_federal_enumerated_powers", check_federal_enumerated_powers),
        ("check_tenth_amendment_reserved_powers", check_tenth_amendment_reserved_powers),
        ("check_supremacy_clause_preemption", check_supremacy_clause_preemption),
        ("check_concurrent_powers_exercisable", check_concurrent_powers_exercisable),
        ("check_tenth_amendment_violation_detection", check_tenth_amendment_violation_detection),
        ("check_power_category_assignments", check_power_category_assignments),
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
    print("All D_FEDERALISM invariants: PASS")
