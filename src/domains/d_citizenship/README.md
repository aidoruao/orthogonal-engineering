---
tags: [src, domains, d-citizenship, readme]
register: technical
---

# D_CITIZENSHIP: Citizenship & Naturalization

**Layer:** 1 (Constitutional)  
**CardinalStrength:** INACCESSIBLE  
**Authority:** 14th Amendment, Article I Section 8

## Description

Domain implementing 14th Amendment birthright citizenship (jus soli) and
naturalization process. Ensures no denaturalization without due process.

## Invariants

1. **14th Amendment Birthright**: All persons born on US soil are citizens.

2. **Naturalization Residency**: Naturalization requires residency (typically
5 years as lawful permanent resident).

3. **Birthright Immunity**: Birthright citizenship cannot be revoked, only
renounced by the citizen.

4. **Due Process Protection**: Denaturalization requires due process
(notice + hearing).

## Key Classes

- `CitizenshipChecker`: Citizenship and naturalization checker
- `Citizen`: A US citizen with constitutional protections
- `NaturalizationProcess`: Naturalization application process
- `BirthrightStatus`: Type of birthright citizenship

## Usage

```python
from datetime import datetime
from src.domains.d_citizenship import CitizenshipChecker

checker = CitizenshipChecker()

# Register birthright citizen
birthright = checker.register_birthright_citizen(
    citizen_id="C001",
    name="Jane Doe",
    birth_date=datetime(1990, 1, 1),
    birthplace="US",
)

# Start naturalization
process = checker.start_naturalization(
    applicant_id="A001",
    lawful_permanent_resident=True,
    years_of_residency=5,
)

# Check denaturalization (requires due process)
result = checker.attempt_denaturalization(
    citizen_id="A001",
    due_process_notice=True,
    due_process_hearing=True,
)
```

## Biblical Inspiration

Leviticus 19:34 — "The foreigner residing among you must be treated as your
native-born. Love them as yourself, for you were foreigners in Egypt."

The 14th Amendment's birthright citizenship reflects the biblical principle
of equal treatment for the foreign-born who reside among us.

## Falsification Tests

- `F_CITIZENSHIP_001`: Verify 14th Amendment birthright citizenship
- `F_CITIZENSHIP_002`: Verify naturalization residency requirement
- `F_CITIZENSHIP_003`: Verify naturalization eligibility criteria
- `F_CITIZENSHIP_004`: Verify birthright citizen denaturalization immunity
- `F_CITIZENSHIP_005`: Verify due process for denaturalization
- `F_CITIZENSHIP_006`: Verify birthright citizenship function
- `F_CITIZENSHIP_007`: Verify 14th Amendment law compliance
