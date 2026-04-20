---
tags: [src, domains, d-family-law, readme]
register: technical
---

# D_FAMILY_LAW: Family Law

**Layer:** 2 (Statutory)  
**CardinalStrength:** PREDICATIVE  
**Authority:** Uniform Marriage and Divorce Act (UMDA), Child Support Standards Act,
State custody statutes, ICPC (Interstate Compact on Placement of Children)

## Description

Domain implementing family law principles including custody determinations
under the "best interest of the child" standard, child support calculations
using the income shares model, and parenting time adjustments. Family law
prioritizes child welfare over parental preferences.

## Invariants

1. **Best Interest Standard**: All custody decisions must prioritize child's
   best interest over parental convenience.

2. **Domestic Violence Consideration**: Evidence of domestic violence weighs
   heavily against custody for the perpetrator.

3. **Support Increases with Income**: Child support obligation increases
   with obligor's income (holding other factors constant).

4. **Support Increases with Children**: More children result in higher
   total support obligation.

5. **Parenting Time Adjustment**: Increased parenting time reduces support
   obligation (shared custody adjustment).

6. **Mature Child Preferences**: Courts consider preferences of mature children
   (typically age 14+) with appropriate weight.

7. **Income Proportional Shares**: Each parent's support share is proportional
   to their percentage of combined income.

## Key Classes

- `BestInterestAnalyzer`: Evaluates custody factors per best interest standard
- `ChildSupportCalculator`: Calculates support using income shares model
- `FamilyLawComplianceChecker`: Validates custody and support arrangements
- `CustodyEvaluation`: Scores parents on custody factors
- `Parent`: Parent with income and parenting time
- `Child`: Child with age, needs, and preferences

## Usage

```python
from fractions import Fraction
from src.domains.d_family_law import (
    BestInterestAnalyzer,
    ChildSupportCalculator,
    CustodyEvaluation,
    Parent,
    Child,
    CustodyFactor,
)

# Create parents and child
mother = Parent(name="Mother", parent_id="P1", annual_income=Fraction(60_000))
father = Parent(name="Father", parent_id="P2", annual_income=Fraction(40_000))
child = Child(name="Child", child_id="C1", age=12)

# Custody evaluation
evaluation = CustodyEvaluation(
    child=child,
    parents=[mother, father],
)
evaluation.score_parent_on_factor("P1", CustodyFactor.STABILITY, 8)
evaluation.score_parent_on_factor("P2", CustodyFactor.STABILITY, 6)

analyzer = BestInterestAnalyzer()
result = analyzer.evaluate_best_interest(evaluation)

print(f"Recommendation: {result['recommendation']}")

# Child support
calculator = ChildSupportCalculator()
support_result = calculator.calculate_support(
    parents=[mother, father],
    children=[child],
    custodial_parent_id="P1",
)

print(f"Monthly support: ${float(support_result['monthly_obligation']):,.2f}")
```

## Biblical Inspiration

Psalm 127:3 — "Children are a heritage from the LORD, offspring a reward from him."

Family law treats children as gifts to be protected and nurtured, not as
possessions to be allocated. The best interest standard reflects the biblical
mandate to care for the vulnerable and prioritize their welfare over adult
conflicts or convenience.

## Falsification Tests

- `F_FAMILY_001`: Verify domestic violence flagged in custody analysis
- `F_FAMILY_002`: Verify higher income produces higher support
- `F_FAMILY_003`: Verify more children increases support obligation
- `F_FAMILY_004`: Verify parenting time reduces support
- `F_FAMILY_005`: Verify mature child preferences weighted appropriately
