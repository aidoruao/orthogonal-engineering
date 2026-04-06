# D_INTERNATIONAL_HUMANITARIAN: International Humanitarian Law

**Layer:** 0 (Supranational)  
**CardinalStrength:** MAHLO  
**Authority:** Geneva Conventions (1949) and Additional Protocols

## Description

Domain implementing International Humanitarian Law (IHL) principles including
distinction, proportionality, and military necessity.

## Invariants

1. **Distinction Principle**: Civilian targets are never lawful; only combatants
may be targeted.

2. **Proportionality**: Military gain must exceed civilian harm for an attack
to be proportional.

3. **Exact Fraction Arithmetic**: All calculations use `fractions.Fraction` for
precise representation (no floating point errors).

## Key Classes

- `IHLChecker`: IHL compliance checker with distinction and proportionality checks
- `UseOfForceEvaluation`: Evaluation of use of force with military/civilian comparison

## Usage

```python
from fractions import Fraction
from src.domains.d_intl_humanitarian import IHLChecker, UseOfForceEvaluation

checker = IHLChecker()

# Check distinction principle
lawful_target = checker.check_distinction(
    target_is_combatant=True,
    civilian_presence=True,  # Must then check proportionality
)

# Check proportionality
evaluation = UseOfForceEvaluation(
    military_objective_value=Fraction(100, 1),
    civilian_harm_risk=Fraction(10, 1),
)
is_proportional = evaluation.is_proportional()  # True: 100 > 10
```

## Biblical Inspiration

Deuteronomy 20:19 — "When you lay siege to a city for a long time, fighting
against it to capture it, do not destroy its trees by putting an ax to them,
because you can eat their fruit."

The principle of distinction and limitation of warfare appears in Scripture,
protecting non-combatants and necessary resources even in conflict.

## Falsification Tests

- `F_INTL_HUMANITARIAN_001`: Verify distinction principle prohibits civilian targeting
- `F_INTL_HUMANITARIAN_002`: Verify proportionality calculation (military > civilian)
- `F_INTL_HUMANITARIAN_003`: Verify exact fraction arithmetic (no floating point)
