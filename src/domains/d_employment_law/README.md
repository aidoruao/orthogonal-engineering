# D_EMPLOYMENT_LAW — Employment Law

**Layer:** 2 (Statutory)  
**Domain:** Employment Law — Title VII, ADA, ADEA, FMLA, Wage/Hour  
**CardinalStrength:** PREDICATIVE

## Overview

Implements employment law including:

- **Title VII (42 U.S.C. §2000e):** Prohibits discrimination based on race, color, religion, sex, national origin
- **ADA (42 U.S.C. §12101):** Requires reasonable accommodation for disabilities
- **ADEA (29 U.S.C. §621):** Prohibits age discrimination (40+)
- **FMLA (29 U.S.C. §2601):** Provides 12 weeks unpaid leave for qualifying reasons
- **FLSA:** Minimum wage, overtime, child labor

Imports from D_LABOR_RIGHTS: NLRA protections for non-supervisory employees.

## Key Components

### Title VII Analysis
- **Prima Facie Case:** Protected class, qualification, adverse action, comparator
- **Disparate Treatment:** Intentional discrimination
- **Disparate Impact:** Neutral policy with discriminatory effect (80% rule)
- **Retaliation:** Protected activity → adverse action (temporal proximity)

### ADA Accommodations
- **Interactive Process:** Required good-faith engagement
- **Reasonable Accommodation:** Effective and not undue hardship
- **Undue Hardship:** Significant difficulty or expense

### FMLA Leave
- **Eligibility:** 12 months employment + 1,250 hours
- **Qualifying Reasons:** Birth, adoption, serious health condition, military
- **Protection:** Job restoration, health insurance continuation

### Wage/Hour (FLSA)
- **Minimum Wage:** $7.25 federal
- **Overtime:** 1.5x rate after 40 hours
- **Wage Theft Detection:** Unpaid hours, misclassification

## Usage

```python
from src.domains.d_employment_law import (
    TitleVIIAnalyzer,
    Employee,
    DiscriminationClaim,
    EmploymentAction,
)

# Create employee
employee = Employee(
    employee_id="E001",
    name="Jane Doe",
    hire_date=datetime(2020, 1, 1),
    protected_classes={ProtectedClass.SEX},
)

# Analyze potential discrimination
action = EmploymentAction(
    action_id="A001",
    employee=employee,
    action_type=EmploymentActionType.TERMINATION,
    action_date=datetime(2024, 6, 1),
)

analyzer = TitleVIIAnalyzer()
```

## Biblical Foundation

> "Look! The wages you failed to pay the workers... are crying out against you."  
> — James 5:4

> "Do not hold back the wages of a hired worker overnight."  
> — Leviticus 19:13

Employment law reflects biblical commands for fair wages and just treatment
of workers. The "laborer is worthy of his hire" (Luke 10:7).

## Files

- `implementation.py` — Core employment law logic
- `invariants.py` — Executable invariant checks (5+ checks)
- `__init__.py` — Public exports
- `README.md` — This documentation

## See Also

- Layer 2: `D_LABOR_RIGHTS` — NLRA, collective bargaining
- Layer 1: `D_DUE_PROCESS` — Employment termination procedures
- Layer 1: `D_EQUAL_PROTECTION` — Anti-discrimination constitutional basis
