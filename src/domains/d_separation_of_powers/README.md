# D_SEPARATION_OF_POWERS: Separation of Powers

**Layer:** 1 (Constitutional)  
**CardinalStrength:** INACCESSIBLE  
**Authority:** US Constitution Articles I-III

## Description

Domain implementing separation of powers checks between executive, legislative,
and judicial branches. Ensures no branch exercises powers belonging to another
branch and enforces the non-delegation doctrine.

## Invariants

1. **Executive Cannot Legislate**: The executive branch cannot create laws;
that power belongs to the legislature.

2. **Legislature Cannot Adjudicate**: The legislature cannot decide specific
cases; that power belongs to the judiciary.

3. **Judiciary Cannot Enforce**: The judiciary cannot directly enforce laws;
that power belongs to the executive.

4. **Non-Delegation Doctrine**: Legislative power cannot be delegated to other
branches.

## Key Classes

- `BranchAuthority`: Authority and powers of a government branch
- `SeparationOfPowersChecker`: Comprehensive separation of powers checker
- `PowerExercise`: Record of a branch exercising a power
- `SeparationViolation`: Enum of separation violations

## Usage

```python
from src.domains.d_separation_of_powers import (
    SeparationOfPowersChecker,
    GovernmentPower,
)

checker = SeparationOfPowersChecker()

# Check executive action
result = checker.check_executive_action(
    power=GovernmentPower.MAKING_LAWS,
    description="Executive order creating penalties",
    claimed_authority="Emergency powers",
)

# Check legislative action
result = checker.check_legislative_action(
    power=GovernmentPower.INTERPRETING_LAWS,
    description="Reversing court decision",
    claimed_authority="Oversight",
)

# Check judicial action
result = checker.check_judicial_action(
    power=GovernmentPower.ENFORCING_LAWS,
    description="Direct arrest order",
    claimed_authority="Contempt power",
)
```

## Biblical Inspiration

Isaiah 33:22 — "For the LORD is our judge, the LORD is our lawgiver, the LORD
is our king; it is he who will save us."

The separation of powers reflects the distinct roles even within divine
authority—judgment, legislation, and kingship—suggesting human government
should maintain these separations to limit the concentration of power.

## Falsification Tests

- `F_SOP_001`: Verify executive cannot legislate
- `F_SOP_002`: Verify legislature cannot adjudicate
- `F_SOP_003`: Verify judiciary cannot enforce
- `F_SOP_004`: Verify proper powers are allowed
- `F_SOP_005`: Verify non-delegation doctrine
- `F_SOP_006`: Verify branch self-identification of powers
