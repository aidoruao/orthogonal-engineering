"""D_FEDERALISM invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: US Constitution Articles I, VI, 10th Amendment
"""

from src.domains.d_federalism.implementation import (
    FederalismChecker,
    GovernmentLevel,
    PowerType,
    SupremacyClause,
    FEDERAL_POWERS,
    STATE_POWERS,
    check_federalism_compliance,
)


def check_federal_can_exercise_enumerated_powers() -> bool:
    """
    Invariant: Federal government can exercise enumerated powers.
    Falsification: If federal exercise of commerce power is rejected.
    """
    checker = FederalismChecker()
    
    result = checker.check_federal_power(
        power=PowerType.REGULATE_INTERSTATE_COMMERCE,
        description="Regulating interstate commerce",
    )
    assert result is True, (
        "Federal regulation of interstate commerce should be constitutional"
    )
    
    return True


def check_federal_cannot_exercise_state_powers() -> bool:
    """
    Invariant: Federal government cannot exercise reserved state powers.
    Falsification: If federal education mandate is accepted.
    """
    checker = FederalismChecker()
    
    result = checker.check_federal_power(
        power=PowerType.EDUCATION,  # Reserved to states
        description="Federal education curriculum mandate",
    )
    assert result is False, (
        "Federal education mandate should violate 10th Amendment"
    )
    
    return True


def check_state_can_exercise_reserved_powers() -> bool:
    """
    Invariant: States can exercise reserved powers (10th Amendment).
    Falsification: If state police power is rejected.
    """
    checker = FederalismChecker()
    
    result = checker.check_state_power(
        power=PowerType.POLICE_POWER,
        description="State police enforcing local laws",
    )
    assert result is True, (
        "State police power should be constitutional"
    )
    
    return True


def check_supremacy_clause_federal_prevails() -> bool:
    """
    Invariant: Federal law prevails in conflicts (Supremacy Clause).
    Falsification: If state law prevails over conflicting federal law.
    """
    checker = FederalismChecker()
    
    resolution = checker.check_supremacy(
        federal_law="Federal Environmental Standard",
        state_law="State Environmental Standard (weaker)",
        conflict_description="State standard conflicts with federal",
    )
    
    assert resolution["supremacy_applies"] is True, (
        "Supremacy Clause should apply"
    )
    assert resolution["prevailing_law"] == "Federal Environmental Standard", (
        "Federal law should prevail"
    )
    assert resolution["state_law_invalid"] is True, (
        "Conflicting state law should be invalid"
    )
    
    return True


def check_tenth_amendment_violation_detected() -> bool:
    """
    Invariant: 10th Amendment violations are detected.
    Falsification: If federal overreach into state powers is not flagged.
    """
    checker = FederalismChecker()
    
    violation = checker.is_tenth_amendment_violation(
        federal_action="Federal police force for local crimes",
        power_type=PowerType.POLICE_POWER,
    )
    
    assert violation is True, (
        "Federal police power over local crimes should violate 10th Amendment"
    )
    
    return True


def check_concurrent_powers_allowed() -> bool:
    """
    Invariant: Both levels can exercise concurrent powers.
    Falsification: If concurrent power exercise is rejected.
    """
    checker = FederalismChecker()
    
    # Federal can tax
    result1 = checker.check_federal_power(
        power=PowerType.TAXATION,
        description="Federal income tax",
    )
    assert result1 is True, "Federal taxation should be allowed"
    
    # State can tax
    result2 = checker.check_state_power(
        power=PowerType.TAXATION,
        description="State sales tax",
    )
    assert result2 is True, "State taxation should be allowed"
    
    return True


def check_power_categories_correct() -> bool:
    """
    Invariant: Power categories are correctly assigned.
    Falsification: If enumerated powers are not in FEDERAL_POWERS.
    """
    assert PowerType.REGULATE_INTERSTATE_COMMERCE in FEDERAL_POWERS
    assert PowerType.DECLARE_WAR in FEDERAL_POWERS
    assert PowerType.POLICE_POWER in STATE_POWERS
    assert PowerType.EDUCATION in STATE_POWERS
    
    return True


def run_all_invariants() -> dict:
    """Run all D_FEDERALISM invariants."""
    checks = [
        check_federal_can_exercise_enumerated_powers,
        check_federal_cannot_exercise_state_powers,
        check_state_can_exercise_reserved_powers,
        check_supremacy_clause_federal_prevails,
        check_tenth_amendment_violation_detected,
        check_concurrent_powers_allowed,
        check_power_categories_correct,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_FEDERALISM invariants: PASS")
