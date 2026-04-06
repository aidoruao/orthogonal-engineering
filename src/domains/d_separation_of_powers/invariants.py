"""D_SEPARATION_OF_POWERS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: US Constitution Articles I-III
"""

from src.domains.d_separation_of_powers.implementation import (
    Branch,
    GovernmentPower,
    BranchAuthority,
    SeparationOfPowersChecker,
    SeparationViolation,
    check_non_delegation_doctrine as check_delegation_validity,
)


def check_executive_cannot_legislate() -> bool:
    """
    Invariant: Executive cannot exercise legislative power (law-making).
    Falsification: If executive making laws is not flagged as violation.
    """
    checker = SeparationOfPowersChecker()
    
    result = checker.check_executive_action(
        power=GovernmentPower.MAKING_LAWS,
        description="Executive order creating new criminal penalties",
        claimed_authority="Emergency powers",
    )
    
    assert not result.constitutional, (
        "Executive legislating should be unconstitutional"
    )
    assert SeparationViolation.EXECUTIVE_LEGISLATING in result.violations, (
        "Executive legislating violation should be flagged"
    )
    
    return True


def check_legislature_cannot_adjudicate() -> bool:
    """
    Invariant: Legislature cannot exercise judicial power (adjudication).
    Falsification: If legislature adjudicating specific cases is not flagged.
    """
    checker = SeparationOfPowersChecker()
    
    result = checker.check_legislative_action(
        power=GovernmentPower.INTERPRETING_LAWS,
        description="Congressional resolution reversing specific court decision",
        claimed_authority="Oversight authority",
    )
    
    assert not result.constitutional, (
        "Legislature adjudicating should be unconstitutional"
    )
    assert SeparationViolation.LEGISLATURE_ADJUDICATING in result.violations, (
        "Legislature adjudicating violation should be flagged"
    )
    
    return True


def check_judiciary_cannot_enforce() -> bool:
    """
    Invariant: Judiciary cannot exercise executive power (enforcement).
    Falsification: If judiciary enforcing laws directly is not flagged.
    """
    checker = SeparationOfPowersChecker()
    
    result = checker.check_judicial_action(
        power=GovernmentPower.ENFORCING_LAWS,
        description="Court ordering direct arrest without warrant",
        claimed_authority="Contempt power",
    )
    
    assert not result.constitutional, (
        "Judiciary enforcing should be unconstitutional"
    )
    assert SeparationViolation.JUDICIARY_ENFORCING in result.violations, (
        "Judiciary enforcing violation should be flagged"
    )
    
    return True


def check_proper_powers_allowed() -> bool:
    """
    Invariant: Each branch can exercise its own proper powers.
    Falsification: If proper power exercise is flagged as violation.
    """
    checker = SeparationOfPowersChecker()
    
    # Executive can enforce laws
    result = checker.check_executive_action(
        power=GovernmentPower.ENFORCING_LAWS,
        description="Prosecuting criminal case",
        claimed_authority="Article II",
    )
    assert result.constitutional, (
        "Executive enforcing laws should be constitutional"
    )
    
    # Legislature can make laws
    result = checker.check_legislative_action(
        power=GovernmentPower.MAKING_LAWS,
        description="Passing new statute",
        claimed_authority="Article I",
    )
    assert result.constitutional, (
        "Legislature making laws should be constitutional"
    )
    
    # Judiciary can interpret laws
    result = checker.check_judicial_action(
        power=GovernmentPower.INTERPRETING_LAWS,
        description="Deciding case on statutory interpretation",
        claimed_authority="Article III",
    )
    assert result.constitutional, (
        "Judiciary interpreting laws should be constitutional"
    )
    
    return True


def check_legislative_non_delegation() -> bool:
    """
    Invariant: Legislative power cannot be delegated to other branches.
    Falsification: If delegation of law-making power is allowed.
    """
    # Delegating law-making to executive is unconstitutional
    result = check_delegation_validity(
        legislative_power=GovernmentPower.MAKING_LAWS,
        delegated_to=Branch.EXECUTIVE,
    )
    assert not result, (
        "Delegating legislative power to executive should violate non-delegation"
    )
    
    # Keeping law-making in legislature is constitutional
    result = check_delegation_validity(
        legislative_power=GovernmentPower.MAKING_LAWS,
        delegated_to=Branch.LEGISLATIVE,
    )
    assert result, (
        "Legislature retaining law-making power should be constitutional"
    )
    
    return True


def check_branch_can_verify_own_powers() -> bool:
    """
    Invariant: BranchAuthority correctly identifies valid powers.
    Falsification: If branch reports it cannot exercise assigned power.
    """
    executive = BranchAuthority(Branch.EXECUTIVE)
    
    assert executive.can_exercise(GovernmentPower.ENFORCING_LAWS), (
        "Executive should be able to enforce laws"
    )
    assert executive.can_exercise(GovernmentPower.COMMANDING_MILITARY), (
        "Executive should be able to command military"
    )
    assert not executive.can_exercise(GovernmentPower.MAKING_LAWS), (
        "Executive should not be able to make laws"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_SEPARATION_OF_POWERS invariants."""
    checks = [
        check_executive_cannot_legislate,
        check_legislature_cannot_adjudicate,
        check_judiciary_cannot_enforce,
        check_proper_powers_allowed,
        check_legislative_non_delegation,
        check_branch_can_verify_own_powers,
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
    print("All D_SEPARATION_OF_POWERS invariants: PASS")
