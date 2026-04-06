"""Falsification tests for D_FAMILY_LAW"""
from fractions import Fraction
from src.domains.d_family_law import (
    BestInterestAnalyzer,
    ChildSupportCalculator,
    CustodyEvaluation,
    Parent,
    Child,
    CustodyFactor,
    calculate_child_support,
)


def test_best_interest_considers_domestic_violence():
    """Domestic violence factor affects custody recommendation."""
    analyzer = BestInterestAnalyzer()
    
    child = Child(name="Child", child_id="C001", age=10)
    parent1 = Parent(name="Parent1", parent_id="P1", annual_income=Fraction(60000))
    parent2 = Parent(name="Parent2", parent_id="P2", annual_income=Fraction(50000))
    
    evaluation = CustodyEvaluation(
        child=child,
        parents=[parent1, parent2],
    )
    
    # Score parent2 low on domestic violence (indicating issue)
    evaluation.score_parent_on_factor("P2", CustodyFactor.DOMESTIC_VIOLENCE, 2)
    evaluation.score_parent_on_factor("P1", CustodyFactor.DOMESTIC_VIOLENCE, 9)
    
    result = analyzer.evaluate_best_interest(evaluation)
    
    # Should have concern about domestic violence
    assert any("violence" in c.lower() for c in result["concerns"])


def test_child_support_increases_with_income():
    """Higher combined income results in higher child support."""
    calculator = ChildSupportCalculator()
    
    low_income_parents = [
        Parent(name="P1", parent_id="P1", annual_income=Fraction(40000)),
        Parent(name="P2", parent_id="P2", annual_income=Fraction(40000)),
    ]
    
    high_income_parents = [
        Parent(name="P1", parent_id="P1", annual_income=Fraction(100000)),
        Parent(name="P2", parent_id="P2", annual_income=Fraction(100000)),
    ]
    
    children = [Child(name="Child", child_id="C1", age=10)]
    
    low_support = calculator.calculate_support(low_income_parents, children, "P2")
    high_support = calculator.calculate_support(high_income_parents, children, "P2")
    
    assert high_support["monthly_obligation"] > low_support["monthly_obligation"]


def test_parenting_time_reduces_support():
    """More parenting time for non-custodial parent reduces support."""
    calculator = ChildSupportCalculator()
    
    base_obligation = Fraction(1000)
    
    # Low parenting time (10%)
    low_time_parent = Parent(
        name="Parent",
        parent_id="P1",
        annual_income=Fraction(60000),
        overnight_nights=36,  # ~10%
    )
    low_adjusted = calculator.adjust_for_parenting_time(base_obligation, low_time_parent)
    
    # High parenting time (45%)
    high_time_parent = Parent(
        name="Parent",
        parent_id="P1",
        annual_income=Fraction(60000),
        overnight_nights=164,  # ~45%
    )
    high_adjusted = calculator.adjust_for_parenting_time(base_obligation, high_time_parent)
    
    assert high_adjusted < low_adjusted


def test_child_support_calculation():
    """Child support calculated correctly with income shares model."""
    result = calculate_child_support(
        parent1_income=Fraction(60000),
        parent2_income=Fraction(40000),
        num_children=2,
    )
    
    assert result["monthly"] > 0
    assert result["annual"] == result["monthly"] * 12


if __name__ == "__main__":
    test_best_interest_considers_domestic_violence()
    test_child_support_increases_with_income()
    test_parenting_time_reduces_support()
    test_child_support_calculation()
    print("All D_FAMILY_LAW tests: PASS")
