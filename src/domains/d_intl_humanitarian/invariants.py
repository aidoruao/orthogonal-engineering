"""D_INTERNATIONAL_HUMANITARIAN invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Geneva Conventions (1949) and Additional Protocols
"""

from fractions import Fraction
from src.domains.d_intl_humanitarian.implementation import (
    IHLChecker,
    UseOfForceEvaluation,
)


def check_distinction_principle() -> bool:
    """
    Invariant: Civilian targets are never lawful under distinction principle.
    Falsification: If check_distinction returns True for non-combatant target.
    """
    checker = IHLChecker()
    
    # Cannot target civilians
    assert not checker.check_distinction(
        target_is_combatant=False,
        civilian_presence=False,
    ), "Should not allow targeting non-combatants"
    
    # Can target combatants
    assert checker.check_distinction(
        target_is_combatant=True,
        civilian_presence=False,
    ), "Should allow targeting combatants"
    
    # Can target combatants even with civilian presence (proportionality check needed)
    assert checker.check_distinction(
        target_is_combatant=True,
        civilian_presence=True,
    ), "Should allow targeting combatants even with civilian presence"
    
    return True


def check_proportionality_principle() -> bool:
    """
    Invariant: Military gain must exceed civilian harm for proportional attack.
    Falsification: If is_proportional returns True when civilian_harm >= military_gain.
    """
    # Proportional: military gain > civilian harm
    proportional = UseOfForceEvaluation(
        military_objective_value=Fraction(10, 1),
        civilian_harm_risk=Fraction(1, 1),
    )
    assert proportional.is_proportional(), (
        "Attack with military gain 10x civilian harm should be proportional"
    )
    
    # Not proportional: civilian harm > military gain
    not_proportional = UseOfForceEvaluation(
        military_objective_value=Fraction(1, 1),
        civilian_harm_risk=Fraction(10, 1),
    )
    assert not not_proportional.is_proportional(), (
        "Attack with civilian harm 10x military gain should not be proportional"
    )
    
    # Edge case: equal values (military_gain > civilian_harm required)
    equal_eval = UseOfForceEvaluation(
        military_objective_value=Fraction(5, 1),
        civilian_harm_risk=Fraction(5, 1),
    )
    assert not equal_eval.is_proportional(), (
        "Attack with equal military gain and civilian harm should not be proportional"
    )
    
    return True


def check_checker_proportionality_method() -> bool:
    """
    Invariant: IHLChecker.check_proportionality matches UseOfForceEvaluation logic.
    Falsification: If checker returns different result than direct evaluation.
    """
    checker = IHLChecker()
    
    # Test via checker method
    assert checker.check_proportionality(
        military_gain=Fraction(100, 1),
        civilian_harm=Fraction(1, 1),
    ), "Checker should confirm high military gain vs low harm is proportional"
    
    assert not checker.check_proportionality(
        military_gain=Fraction(1, 10),
        civilian_harm=Fraction(10, 1),
    ), "Checker should reject low military gain vs high harm"
    
    return True


def check_fraction_precision() -> bool:
    """
    Invariant: Proportionality uses exact Fraction arithmetic, not floating point.
    Falsification: If Fraction calculations are imprecise.
    """
    # Use fractions that would be imprecise in floating point
    eval1 = UseOfForceEvaluation(
        military_objective_value=Fraction(1, 3),
        civilian_harm_risk=Fraction(1, 7),
    )
    
    # 1/3 > 1/7, so should be proportional
    assert eval1.is_proportional(), (
        "1/3 > 1/7 should be proportional using exact fraction arithmetic"
    )
    
    eval2 = UseOfForceEvaluation(
        military_objective_value=Fraction(1, 10),
        civilian_harm_risk=Fraction(1, 3),
    )
    
    # 1/10 < 1/3, so should not be proportional
    assert not eval2.is_proportional(), (
        "1/10 < 1/3 should not be proportional"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_INTERNATIONAL_HUMANITARIAN invariants."""
    checks = [
        check_distinction_principle,
        check_proportionality_principle,
        check_checker_proportionality_method,
        check_fraction_precision,
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
    print("All D_INTERNATIONAL_HUMANITARIAN invariants: PASS")
