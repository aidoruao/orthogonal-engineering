"""D_INTERNATIONAL_CRIMINAL invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Rome Statute of the International Criminal Court (1998)
"""

from src.domains.d_intl_criminal.implementation import (
    InternationalCriminalLaw,
    UniversalJurisdictionCase,
    CoreCrime,
)


def check_universal_jurisdiction_for_core_crimes() -> bool:
    """
    Invariant: Core crimes (genocide, crimes against humanity, war crimes, aggression)
    are subject to universal jurisdiction when evidence is present.
    Falsification: If can_prosecute returns False for core crime with evidence.
    """
    icl = InternationalCriminalLaw()
    
    # Test each core crime
    for crime in CoreCrime:
        case = UniversalJurisdictionCase(
            case_id=f"TEST-{crime.name}",
            crime=crime,
            suspect=f"Suspect {crime.name}",
            location="Foreign territory",
            evidence_present=True,
        )
        
        assert case.can_prosecute(), (
            f"Core crime {crime.name} with evidence should be prosecutable under universal jurisdiction"
        )
    
    return True


def check_no_prosecution_without_evidence() -> bool:
    """
    Invariant: Cases without evidence cannot be prosecuted.
    Falsification: If can_prosecute returns True when evidence_present is False.
    """
    case = UniversalJurisdictionCase(
        case_id="TEST-NO-EVIDENCE",
        crime=CoreCrime.WAR_CRIMES,
        suspect="Unknown Suspect",
        location="Unknown location",
        evidence_present=False,
    )
    
    assert not case.can_prosecute(), (
        "Case without evidence should not be prosecutable"
    )
    
    return True


def check_icc_complementarity_principle() -> bool:
    """
    Invariant: ICC can only prosecute if domestic court is unwilling or unable.
    Falsification: If check_complementarity returns True when domestic proceedings
    are adequate (willing and able).
    """
    icl = InternationalCriminalLaw()
    
    # Domestic proceedings adequate: ICC cannot prosecute
    assert not icl.check_complementarity(
        domestic_proceedings=True,
        domestic_willing=True,
        domestic_able=True,
    ), "ICC should not prosecute when domestic proceedings are adequate"
    
    # No domestic proceedings: ICC can prosecute
    assert icl.check_complementarity(
        domestic_proceedings=False,
        domestic_willing=False,
        domestic_able=False,
    ), "ICC should prosecute when no domestic proceedings"
    
    # Domestic proceedings exist but unwilling (shielding): ICC can prosecute
    assert icl.check_complementarity(
        domestic_proceedings=True,
        domestic_willing=False,
        domestic_able=True,
    ), "ICC should prosecute when domestic court is unwilling"
    
    # Domestic proceedings exist but unable: ICC can prosecute
    assert icl.check_complementarity(
        domestic_proceedings=True,
        domestic_willing=True,
        domestic_able=False,
    ), "ICC should prosecute when domestic court is unable"
    
    return True


def check_all_core_crimes_defined() -> bool:
    """
    Invariant: All four core crimes under Rome Statute are defined.
    Falsification: If CoreCrime enum does not contain exactly 4 crimes.
    """
    expected_crimes = {
        CoreCrime.GENOCIDE,
        CoreCrime.CRIMES_AGAINST_HUMANITY,
        CoreCrime.WAR_CRIMES,
        CoreCrime.AGGRESSION,
    }
    
    actual_crimes = set(CoreCrime)
    
    assert actual_crimes == expected_crimes, (
        f"Expected crimes {expected_crimes}, got {actual_crimes}"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_INTERNATIONAL_CRIMINAL invariants."""
    checks = [
        check_universal_jurisdiction_for_core_crimes,
        check_no_prosecution_without_evidence,
        check_icc_complementarity_principle,
        check_all_core_crimes_defined,
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
    print("All D_INTERNATIONAL_CRIMINAL invariants: PASS")
