"""D_CRIMINAL_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Statutory criminal law, constitutional due process
"""

from fractions import Fraction
from src.domains.d_criminal_law.implementation import (
    CriminalLaw,
    CriminalOffense,
    OffenseClass,
    BurdenOfProof,
    Sentencing,
    check_nullum_crimen,
)


def check_nullum_crimen_sine_lege() -> bool:
    """
    Invariant: No punishment without prior law (nullum crimen sine lege).
    Falsification: If prosecution proceeds for undefined offense.
    """
    law = CriminalLaw()
    
    # Try to prosecute undefined offense
    result = law.prosecute(
        defendant="Defendant A",
        offense_name="Unknown Crime",
        evidence=["some evidence"],
    )
    
    assert result["verdict"] == "DISMISSED", (
        "Prosecution of undefined offense should be dismissed"
    )
    assert result["nullum_crimen_violation"] is True
    
    return True


def check_burden_of_proof_on_prosecution() -> bool:
    """
    Invariant: Burden of proof is on prosecution.
    Falsification: If defendant convicted without prosecution meeting burden.
    """
    law = CriminalLaw()
    
    # Define offense
    law.define_offense(
        offense_name="Theft",
        statute_citation="Penal Code § 484",
        offense_class=OffenseClass.MISDEMEANOR,
        elements=["taking", "property of another", "intent to steal"],
        max_penalty_years=1,
        max_fine=Fraction(1000),
    )
    
    # Prosecute with insufficient evidence
    result = law.prosecute(
        defendant="Defendant B",
        offense_name="Theft",
        evidence=["single witness"],  # Insufficient
    )
    
    assert result["verdict"] == "NOT GUILTY", (
        "Should acquit when burden of proof not met"
    )
    assert result["burden_met"] is False
    
    return True


def check_conviction_requires_proof_beyond_doubt() -> bool:
    """
    Invariant: Conviction requires proof beyond reasonable doubt.
    Falsification: If conviction with minimal evidence.
    """
    law = CriminalLaw()
    
    law.define_offense(
        offense_name="Assault",
        statute_citation="Penal Code § 240",
        offense_class=OffenseClass.MISDEMEANOR,
        elements=["attempt", "violent injury", "on another person"],
        max_penalty_years=6,
        max_fine=Fraction(1000),
    )
    
    # Prosecute with strong evidence
    result = law.prosecute(
        defendant="Defendant C",
        offense_name="Assault",
        evidence=["video recording", "witness testimony", "physical evidence"],
    )
    
    assert result["verdict"] == "GUILTY", (
        "Should convict with sufficient evidence"
    )
    assert result["burden_met"] is True
    
    return True


def check_sentencing_within_statutory_range() -> bool:
    """
    Invariant: Sentencing is within statutory range.
    Falsification: If sentence exceeds maximum for offense class.
    """
    law = CriminalLaw()
    
    law.define_offense(
        offense_name="Petty Theft",
        statute_citation="Penal Code § 488",
        offense_class=OffenseClass.MISDEMEANOR,
        elements=["taking property", "value under $950"],
        max_penalty_years=1,
        max_fine=Fraction(1000),
    )
    
    # Attempt to exceed statutory maximum
    result = law.sentence(
        defendant="Defendant D",
        offense_name="Petty Theft",
        base_sentence_years=5,  # Exceeds 1 year max
        fine=Fraction(500),
        mitigating=[],
        aggravating=[],
    )
    
    assert "error" in result, (
        "Should reject sentence exceeding statutory maximum"
    )
    
    return True


def check_mitigating_factors_reduce_sentence() -> bool:
    """
    Invariant: Mitigating factors reduce sentence.
    Falsification: If mitigating factors don't affect sentence.
    """
    offense = CriminalOffense(
        offense_name="Test Offense",
        statute_citation="Test Code § 1",
        offense_class=OffenseClass.MISDEMEANOR,
        max_penalty_years=5,
    )
    
    sentencing = Sentencing(
        offense=offense,
        convicted=True,
        sentence_years=4,
        mitigating_factors=["first offense", "cooperated"],
        aggravating_factors=[],
    )
    
    final = sentencing.apply_sentencing_factors()
    
    assert final < 4, (
        "Mitigating factors should reduce sentence"
    )
    
    return True


def check_aggravating_factors_increase_sentence() -> bool:
    """
    Invariant: Aggravating factors increase sentence.
    Falsification: If aggravating factors don't affect sentence.
    """
    offense = CriminalOffense(
        offense_name="Test Offense",
        statute_citation="Test Code § 1",
        offense_class=OffenseClass.FELONY,
        max_penalty_years=10,
    )
    
    sentencing = Sentencing(
        offense=offense,
        convicted=True,
        sentence_years=5,
        mitigating_factors=[],
        aggravating_factors=["used weapon", "vulnerable victim"],
    )
    
    final = sentencing.apply_sentencing_factors()
    
    assert final > 5, (
        "Aggravating factors should increase sentence"
    )
    
    return True


def check_offense_must_be_defined() -> bool:
    """
    Invariant: Offense must have statute citation and elements.
    Falsification: If offense without statute is considered defined.
    """
    # Properly defined offense
    proper = CriminalOffense(
        offense_name="Proper Offense",
        statute_citation="Code § 123",
        offense_class=OffenseClass.MISDEMEANOR,
        elements=["element 1", "element 2"],
    )
    assert proper.is_defined_by_law() is True
    
    # Improperly defined offense
    improper = CriminalOffense(
        offense_name="Improper Offense",
        statute_citation="",
        offense_class=OffenseClass.MISDEMEANOR,
        elements=[],
    )
    assert improper.is_defined_by_law() is False
    
    return True


def run_all_invariants() -> dict:
    """Run all D_CRIMINAL_LAW invariants."""
    checks = [
        check_nullum_crimen_sine_lege,
        check_burden_of_proof_on_prosecution,
        check_conviction_requires_proof_beyond_doubt,
        check_sentencing_within_statutory_range,
        check_mitigating_factors_reduce_sentence,
        check_aggravating_factors_increase_sentence,
        check_offense_must_be_defined,
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
    print("All D_CRIMINAL_LAW invariants: PASS")
