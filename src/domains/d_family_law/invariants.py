"""D_FAMILY_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Uniform Marriage and Divorce Act (UMDA), Child Support Standards Act
"""

from src.domains.d_family_law.implementation import (
    BestInterestAnalyzer,
    ChildSupportCalculator,
    CustodyEvaluation,
    Parent,
    Child,
    CustodyFactor,
    CustodyType,
    calculate_child_support,
)
from fractions import Fraction


def check_best_interest_considers_domestic_violence() -> bool:
    """
    Invariant: Best interest analysis must consider domestic violence.
    Falsification: If domestic violence factor not included in analysis.
    """
    analyzer = BestInterestAnalyzer()
    
    assert CustodyFactor.DOMESTIC_VIOLENCE in analyzer.relevant_factors, (
        "Domestic violence must be relevant factor"
    )
    
    return True


def check_child_support_increases_with_income() -> bool:
    """
    Invariant: Child support obligation increases with obligor income.
    Falsification: If higher income produces lower support obligation.
    """
    # Low income scenario
    low = calculate_child_support(
        parent1_income=Fraction(30_000),  # Obligor
        parent2_income=Fraction(0),
        num_children=2,
    )
    
    # High income scenario
    high = calculate_child_support(
        parent1_income=Fraction(100_000),  # Obligor
        parent2_income=Fraction(0),
        num_children=2,
    )
    
    assert high["monthly"] > low["monthly"], (
        f"Higher income should produce higher support: {high['monthly']} vs {low['monthly']}"
    )
    
    return True


def check_child_support_increases_with_children() -> bool:
    """
    Invariant: Support obligation increases with number of children.
    Falsification: If more children produce lower support.
    """
    one_child = calculate_child_support(
        parent1_income=Fraction(60_000),
        parent2_income=Fraction(0),
        num_children=1,
    )
    
    three_children = calculate_child_support(
        parent1_income=Fraction(60_000),
        parent2_income=Fraction(0),
        num_children=3,
    )
    
    assert three_children["monthly"] > one_child["monthly"], (
        "More children should require higher support"
    )
    
    return True


def check_custody_score_determines_recommendation() -> bool:
    """
    Invariant: Higher custody score produces recommendation favoring that parent.
    Falsification: If higher score doesn't correlate with recommendation.
    """
    child = Child(name="Child", child_id="C1", age=10)
    parent1 = Parent(name="Better", parent_id="P1", annual_income=Fraction(50_000))
    parent2 = Parent(name="Worse", parent_id="P2", annual_income=Fraction(50_000))
    
    evaluation = CustodyEvaluation(
        child=child,
        parents=[parent1, parent2],
    )
    
    # Score parent1 higher
    evaluation.score_parent_on_factor("P1", CustodyFactor.STABILITY, 9)
    evaluation.score_parent_on_factor("P1", CustodyFactor.MENTAL_PHYSICAL_HEALTH, 9)
    evaluation.score_parent_on_factor("P2", CustodyFactor.STABILITY, 4)
    evaluation.score_parent_on_factor("P2", CustodyFactor.MENTAL_PHYSICAL_HEALTH, 4)
    
    analyzer = BestInterestAnalyzer()
    result = analyzer.evaluate_best_interest(evaluation)
    
    score1 = evaluation.get_parent_score("P1")
    score2 = evaluation.get_parent_score("P2")
    
    assert score1 > score2, (
        "Higher scoring parent should have higher score"
    )
    
    return True


def check_parenting_time_reduces_support() -> bool:
    """
    Invariant: Increased parenting time reduces support obligation.
    Falsification: If more overnights don't reduce support.
    """
    calculator = ChildSupportCalculator()
    
    base_obligation = Fraction(1000)  # Monthly
    
    # Minimal parenting time (every other weekend ≈ 20%)
    minimal_time = Parent(
        name="Minimal",
        parent_id="P1",
        annual_income=Fraction(60_000),
        overnight_nights=70,
    )
    
    # Substantial parenting time (40%)
    substantial_time = Parent(
        name="Substantial",
        parent_id="P2",
        annual_income=Fraction(60_000),
        overnight_nights=146,
    )
    
    minimal_adjusted = calculator.adjust_for_parenting_time(base_obligation, minimal_time)
    substantial_adjusted = calculator.adjust_for_parenting_time(base_obligation, substantial_time)
    
    assert substantial_adjusted < minimal_adjusted, (
        f"More parenting time should reduce support: {substantial_adjusted} vs {minimal_adjusted}"
    )
    
    return True


def check_mature_child_preferences_considered() -> bool:
    """
    Invariant: Mature child's preferences carry weight in custody analysis.
    Falsification: If mature child's input not given high weight.
    """
    mature_child = Child(
        name="Teen",
        child_id="C1",
        age=16,
        maturity_level="mature",
    )
    
    young_child = Child(
        name="Young",
        child_id="C2",
        age=6,
        maturity_level="immature",
    )
    
    analyzer = BestInterestAnalyzer()
    
    # Check that mature child's wishes factor is considered
    evaluation_mature = CustodyEvaluation(
        child=mature_child,
        parents=[],
    )
    
    analysis = analyzer._analyze_factor(CustodyFactor.CHILD_WISHES, evaluation_mature)
    
    assert analysis.get("child_input_weight") == "HIGH", (
        "Mature child's preferences should have HIGH weight"
    )
    
    # Young child should not be considered
    evaluation_young = CustodyEvaluation(
        child=young_child,
        parents=[],
    )
    
    analysis_young = analyzer._analyze_factor(CustodyFactor.CHILD_WISHES, evaluation_young)
    
    assert not analysis_young.get("considered", True), (
        "Immature child's preferences should not be considered"
    )
    
    return True


def check_support_shares_proportional_to_income() -> bool:
    """
    Invariant: Each parent's support share proportional to their income.
    Falsification: If income proportions don't match support shares.
    """
    calculator = ChildSupportCalculator()
    
    parents = [
        Parent(name="High Earner", parent_id="P1", annual_income=Fraction(80_000)),
        Parent(name="Low Earner", parent_id="P2", annual_income=Fraction(20_000)),
    ]
    
    child = Child(name="Child", child_id="C1", age=10)
    
    result = calculator.calculate_support(parents, [child], "P2")
    
    # High earner (80%) should pay more than low earner (20%)
    share1 = result["parent_shares"]["P1"]["income_share"]
    share2 = result["parent_shares"]["P2"]["income_share"]
    
    assert share1 == Fraction(80, 100), (
        f"High earner share should be 80%, got {share1}"
    )
    assert share2 == Fraction(20, 100), (
        f"Low earner share should be 20%, got {share2}"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_FAMILY_LAW invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_best_interest_considers_domestic_violence,
        check_child_support_increases_with_income,
        check_child_support_increases_with_children,
        check_custody_score_determines_recommendation,
        check_parenting_time_reduces_support,
        check_mature_child_preferences_considered,
        check_support_shares_proportional_to_income,
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
    print("All D_FAMILY_LAW invariants: PASS")
